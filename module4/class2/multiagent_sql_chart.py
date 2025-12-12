"""
multiagent_sql_chart.py

Combined LangGraph multi-agent script:
- Custom SQL Agent
- Chart Generator Agent (executes Python to build charts via PythonREPL)
- Agents collaborate by sharing MessagesState; either can return FINAL ANSWER to stop.
"""

import requests
import os
from typing import Literal

from langgraph.graph import MessagesState, StateGraph, START, END
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langgraph.types import Command
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

from dotenv import load_dotenv

load_dotenv()

LLM_SELECTOR = "openai:gpt-4.1"

CHINOOK_URL = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"
CHINOOK_FILENAME = "Chinook.db"

# Limit results returned by SQL agent
TOP_K = 5


def init_llm():
    return init_chat_model(LLM_SELECTOR)


def ensure_chinook_db():
    if not os.path.exists(CHINOOK_FILENAME):
        print(f"Downloading {CHINOOK_FILENAME} ...")
        resp = requests.get(CHINOOK_URL)
        resp.raise_for_status()
        with open(CHINOOK_FILENAME, "wb") as f:
            f.write(resp.content)
        print("Downloaded Chinook.db")


ensure_chinook_db()
db = SQLDatabase.from_uri(f"sqlite:///{CHINOOK_FILENAME}")

llm = init_llm()

# Build toolkit and tools used by the SQL agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
sql_tools = toolkit.get_tools()


def get_tool(name: str):
    return next(t for t in sql_tools if t.name == name)


sql_list_tables_tool = get_tool("sql_db_list_tables")
sql_schema_tool = get_tool("sql_db_schema")
sql_query_checker_tool = get_tool("sql_db_query_checker")
sql_query_tool = get_tool("sql_db_query")


repl = PythonREPL()


@tool
def python_repl_tool(code: str):
    """
    Execute Python code and return stdout or error. If you want to save chart files,
    write them into the working directory and they'll be available after execution.
    """
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )


def make_system_prompt(suffix: str) -> str:
    return (
        "You are a helpful AI assistant, collaborating with another assistant."
        " Use the provided tools to progress towards answering the user's question."
        " If you are unable to fully answer, that's OK — your colleague will continue."
        " If you or your colleague have the final answer or deliverable, prefix your response with FINAL ANSWER."
        f"\n{suffix}"
    )


def sql_list_tables_node(state: MessagesState):
    """
    Produces a tool_call message for sql_db_list_tables, then invokes the tool
    and returns the messages as if the SQL agent produced them.
    """
    tool_call = {
        "name": "sql_db_list_tables",
        "args": {},
        "id": "list_tables_call",
        "type": "tool_call",
    }
    tool_call_message = AIMessage(content="", tool_calls=[tool_call])
    # invoke the actual tool
    tool_message = sql_list_tables_tool.invoke(tool_call)
    # respond summarizing available tables
    response = AIMessage(f"Available tables: {tool_message.content}")
    return {"messages": [tool_call_message, tool_message, response]}


def sql_call_get_schema_node(state: MessagesState):
    """
    Bind the schema tool and let the model decide which tables to query for schemas.
    We will call the LLM with the last user message (and previous context) and
    allow it to return a tool_call to sql_db_schema.
    """
    # Bind schema tool to LLM
    llm_with_tools = llm.bind_tools([sql_schema_tool], tool_choice="any")
    # Pass the messages we have so far to the LLM
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# System prompt for query generation
generate_query_system_prompt = f"""
You are an agent designed to interact with a SQL database.
Given the user's question, create a syntactically correct {db.dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a number of examples, limit results to at most {TOP_K}.
Do NOT perform any DML operations (INSERT/UPDATE/DELETE/DROP).
Always produce a single tool_call named 'sql_db_query' when you generate a query.
"""


def sql_generate_query_node(state: MessagesState):
    # Use LLM bound to sql_query_tool so it can produce a tool_call
    llm_with_tools = llm.bind_tools([sql_query_tool])
    # prepend system message
    system_message = {"role": "system", "content": generate_query_system_prompt}
    response = llm_with_tools.invoke([system_message] + state["messages"])
    return {"messages": [response]}


check_query_system_prompt = f"""
You are a SQL expert. Double check the {db.dialect} query for common mistakes:
- quoting, casting, joins, NOT IN with NULLs, BETWEEN inclusivity, UNION vs UNION ALL, etc.
If mistakes, rewrite query; otherwise reproduce original.
You will produce a tool_call if you want to run the query; otherwise return the corrected query.
"""


def sql_check_query_node(state: MessagesState):
    # The last message should contain a tool_call with query args
    last = state["messages"][-1]
    # If there are no tool calls, just let the model proceed (no-op)
    if not getattr(last, "tool_calls", None):
        # call LLM to possibly produce the same message back
        llm_with_tools = llm.bind_tools([sql_query_tool], tool_choice="any")
        system_message = {"role": "system", "content": check_query_system_prompt}
        # craft a user message containing the query to check if possible
        # attempt to extract query from last content if available
        user_msg = {"role": "user", "content": getattr(last, "content", "")}
        response = llm_with_tools.invoke([system_message, user_msg])
        return {"messages": [response]}
    # If there is a tool_call, create a user message with the query and run the checker LLM
    tool_call = last.tool_calls[0]
    user_message = {"role": "user", "content": tool_call["args"].get("query", "")}
    llm_with_tools = llm.bind_tools([sql_query_tool], tool_choice="any")
    system_message = {"role": "system", "content": check_query_system_prompt}
    response = llm_with_tools.invoke([system_message, user_message])
    # ensure the response keeps the tool_call id so the compiled graph can track it
    response.id = last.id
    return {"messages": [response]}


# The run_query node will execute the query using the tool's invoke directly
def sql_run_query_node(state: MessagesState):
    last = state["messages"][-1]
    if not getattr(last, "tool_calls", None):
        # nothing to run
        return {"messages": [AIMessage("No query to execute.")]}

    tool_call = last.tool_calls[0]
    # call the real sql_db_query tool
    tool_message = sql_query_tool.invoke(tool_call)
    response = AIMessage(f"Query results: {tool_message.content}")
    return {"messages": [tool_call, tool_message, response]}


# Assemble SQL agent as a small state graph (internal flow) implemented as a single callable node
def sql_agent_node(state: MessagesState) -> Command[Literal["chart_generator", END]]:
    """
    Orchestrates the SQL workflow and returns a Command update containing the SQL agent's messages.
    After finishing one cycle (listing tables, schema, generate-check-run), it hands off to
    chart_generator.
    """
    # 1) list tables
    step1 = sql_list_tables_node(state)
    messages_accum = step1["messages"]

    # 2) call get schema (LLM may produce tool_call)
    # Pass current conversation to the LLM so it can reason which tables to inspect
    temp_state = {"messages": state["messages"] + messages_accum}
    step2 = sql_call_get_schema_node(temp_state)
    messages_accum += step2["messages"]

    # If the last produced message contains a tool_call for schema, invoke that tool
    last = messages_accum[-1]
    if getattr(last, "tool_calls", None):
        tc = last.tool_calls[0]
        if tc["name"] == "sql_db_schema":
            tool_message = sql_schema_tool.invoke(tc)
            messages_accum.append(tool_message)
            messages_accum.append(AIMessage("Schema fetched."))
    # 3) generate query
    temp_state = {"messages": state["messages"] + messages_accum}
    step3 = sql_generate_query_node(temp_state)
    messages_accum += step3["messages"]

    # 4) check query (if query tool_call exists)
    last = messages_accum[-1]
    if (
        getattr(last, "tool_calls", None)
        and last.tool_calls[0]["name"] == "sql_db_query"
    ):
        # prepare a temp state and call check
        temp_state = {"messages": state["messages"] + messages_accum}
        step4 = sql_check_query_node(temp_state)
        messages_accum += step4["messages"]
    else:
        # no tool call to check; skip
        pass

    # 5) run query if present
    last = messages_accum[-1]
    if (
        getattr(last, "tool_calls", None)
        and last.tool_calls[0]["name"] == "sql_db_query"
    ):
        tc = last.tool_calls[0]
        tool_message = sql_query_tool.invoke(tc)
        messages_accum.append(tool_message)
        messages_accum.append(AIMessage("Query executed; results returned above."))

    # Build new messages to update global MessagesState: share the full transcript from SQL agent
    # We'll include the detailed internal messages so chart agent has full context
    shared_messages = []
    for m in messages_accum:
        # wrap AIMessage content into HumanMessage with agent name prefixes where appropriate
        if isinstance(m, AIMessage):
            shared_messages.append(HumanMessage(content=m.content, name="sql_agent"))
        else:
            # tool messages can be included as human-readable
            shared_messages.append(
                HumanMessage(content=str(getattr(m, "content", m)), name="sql_agent")
            )

    # Determine goto: if any agent used "FINAL ANSWER" then end
    # For this node, check the final textual outputs for "FINAL ANSWER"
    goto = "chart_generator"
    for m in shared_messages:
        if "FINAL ANSWER" in (m.content or ""):
            goto = END
            break

    # set "messages" to include the agent's internal transcript appended to the incoming state
    return Command(
        update={
            "messages": state["messages"] + shared_messages,
        },
        goto=goto,
    )


def get_next_node(last_message: BaseMessage, goto: str):
    if "FINAL ANSWER" in (last_message.content or ""):
        return END
    return goto


chart_agent = create_agent(
    model=llm,
    tools=[python_repl_tool],
    system_prompt=make_system_prompt(
        "You can only generate charts. ALWAYS start Matplotlib code with:\n"
        "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt\n"
        "You are working with a SQL colleague. ALWAYS respond with FINAL ANSWER."
    ),
)


def chart_node(state: MessagesState) -> Command[Literal["sql_agent", END]]:
    # Let the chart agent run on the shared messages
    result = chart_agent.invoke(state)
    # Decide where to go next
    goto = get_next_node(result["messages"][-1], "sql_agent")
    # wrap last AI message as human message so the SQL agent sees it as collaborator output
    result["messages"][-1] = HumanMessage(
        content=result["messages"][-1].content, name="chart_generator"
    )
    return Command(
        update={
            "messages": result["messages"],
        },
        goto=goto,
    )


workflow = StateGraph(MessagesState)
workflow.add_node("sql_agent", sql_agent_node)
workflow.add_node("chart_generator", chart_node)

workflow.add_edge(START, "sql_agent")

graph = workflow.compile()


if __name__ == "__main__":
    user_question = "Which genre on average has the longest tracks? And plot the top 5 genres by average track length as a bar chart."

    # Seed the MessagesState with the user's question
    initial_state = {"messages": [HumanMessage(content=user_question, name="user")]}

    print("Running multi-agent workflow...\n")
    for step in graph.stream(initial_state, stream_mode="values"):
        # print the last message in the latest step for visibility
        last = step["messages"][-1]
        print("----- STEP -----")
        print(f"{type(last).__name__}: {getattr(last, 'content', repr(last))}\n")
