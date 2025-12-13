"""
Hierarchical team of Agents.
"""
from typing import List, TypedDict, Literal
import statistics
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.managed.is_last_step import RemainingSteps
from dotenv import load_dotenv

load_dotenv()


@tool
def basic_statistics_tool(numbers: List[float]) -> str:
    """
    Calculates mean, median, and mode of a list of numbers.
    """
    try:
        mean = statistics.mean(numbers)
        median = statistics.median(numbers)
        mode = statistics.mode(numbers)
        return f"Mean: {mean}, Median: {median}, Mode: {mode}"
    except Exception as e:
        return f"Error calculating statistics: {e}"

# Explanation:
# Checks if numbers are increasing, decreasing, or stable.
@tool
def trend_detection_tool(numbers: List[float]) -> str:
    """
    Detects if the trend is increasing, decreasing, or stable.
    """
    if len(numbers) < 2:
        return "Not enough data to detect trend."

    increasing = all(x < y for x, y in zip(numbers, numbers[1:]))
    decreasing = all(x > y for x, y in zip(numbers, numbers[1:]))

    if increasing:
        return "Upward trend detected."
    elif decreasing:
        return "Downward trend detected."
    else:
        return "No clear trend detected."

@tool
def summarize_points_tool(text: str) -> str:
    """
    Summarizes a long text into bullet points.
    """
    sentences = text.split(".")
    bullets = [f"- {s.strip()}" for s in sentences if s.strip()]
    return "\n".join(bullets)

@tool
def report_generation_tool(points: List[str]) -> str:
    """
    Takes bullet points and generates a simple market research report.
    """
    intro = "📄 **Market Research Report**\n\n"
    body = "\n".join(points)
    outro = "\n\n🔚 End of Report."

    return intro + body + outro

class State(MessagesState):
    next: str  # Field to store the next agent to call
    remaining_steps: RemainingSteps

llm = init_chat_model("openai:gpt-4.1")

def statistician_agent_node(state: State) -> Command[Literal["supervisor"]]:
    statistician_agent = create_agent(
        model=llm,
        tools=[basic_statistics_tool],
        system_prompt="You are a statistician. Use the provided tool to analyze numerical data and find mean, median, mode. DO NOT write summary. DO NOT generate report."
    )
    result = statistician_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="statistician")
            ]
        },
        goto="supervisor"
    )

def trend_detection_agent_node(state: State) -> Command[Literal["supervisor"]]:
    trend_detection_agent = create_agent(
        model=llm,
        tools=[trend_detection_tool],
        system_prompt="You are a data analyst. Your job is to detect trends (upward or downward) from numerical data.DO NOT write summary. DO NOT generate report."
    )
    result = trend_detection_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="trend_detector")
            ]
        },
        goto="supervisor"
    )

def summarizer_agent_node(state: State) -> Command[Literal["supervisor"]]:
    summarizer_agent = create_agent(
        model=llm,
        tools=[summarize_points_tool],
        system_prompt="You are a content summarizer. Create bullet points from long texts."
    )
    result = summarizer_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="summarizer")
            ]
        },
        goto="supervisor"
    )

def report_writer_agent_node(state: State) -> Command[Literal["supervisor"]]:
    report_writer_agent = create_agent(
        model=llm,
        tools=[report_generation_tool],
        system_prompt="You are a report writer. Create a formal market research report based on the given points."
    )
    result = report_writer_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="report_writer")
            ]
        },
        goto="supervisor"
    )

def make_supervisor_node(llm, members: list[str]) -> str:
    options = ["FINISH"] + members
    system_prompt = (
            "You are a Supervisor responsible for coordinating the following specialized workers: {members}.\n"
            "Based on the user's request and the current conversation history, select the most appropriate worker to handle the next step.\n"
            "Each worker will perform their assigned task and report back with results and status updates.\n"
            "After all necessary tasks have been completed, respond with 'FINISH' to indicate that the workflow is complete.\n"
            "Always choose only one worker at a time, based on the current context and task requirements."
        )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""
        next: Literal[*options]

    def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
        """
        Supervisor decides which worker to activate next.
        """
        if state["remaining_steps"] <= 2:
            return Command(goto=END)
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]

        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]
        if goto == "FINISH":
            goto = END

        return Command(goto=goto, update={"next": goto})

    return supervisor_node

data_team_members = ["statistician", "trend_detector"]
# Create Supervisor for Data Analysis Team
data_analysis_supervisor_node = make_supervisor_node(llm, data_team_members)

content_team_members = ["summarizer", "report_writer"]
# Create Supervisor for Content Writing Team
content_writing_supervisor_node = make_supervisor_node(llm, content_team_members)

# 1. Create a StateGraph for the Data Analysis Team
data_analysis_graph = StateGraph(State)

# 2. Add nodes (Supervisor + Agents)
data_analysis_graph.add_node("statistician",statistician_agent_node )

data_analysis_graph.add_node("trend_detector",trend_detection_agent_node)

data_analysis_graph.add_node("supervisor", data_analysis_supervisor_node)

# 3. Define the edges (how things flow)
data_analysis_graph.add_edge(START, "supervisor")

# 4. Compile the graph
compiled_data_analysis_graph = data_analysis_graph.compile()

# 1. Create a StateGraph for the Content Writing Team
content_writing_graph = StateGraph(State)

# 2. Add nodes (Supervisor + Agents)
content_writing_graph.add_node("summarizer",summarizer_agent_node)

content_writing_graph.add_node("report_writer",report_writer_agent_node)

content_writing_graph.add_node("supervisor", content_writing_supervisor_node)

# 3. Define edges
content_writing_graph.add_edge(START, "supervisor")

# 4. Compile the graph
compiled_content_writing_graph = content_writing_graph.compile()

# Top-Level Supervisor Members
top_team_members = ["data_analysis_team", "content_writing_team"]

# Create Top Supervisor Node
top_supervisor_node = make_supervisor_node(llm, top_team_members)

def call_data_analysis_team(state: State) -> Command[Literal["supervisor"]]:
    response = compiled_data_analysis_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={"messages": [HumanMessage(content=response["messages"][-1].content, name="data_analysis_team")]},
        goto="supervisor"
    )

def call_content_writing_team(state: State) -> Command[Literal["supervisor"]]:
    response = compiled_content_writing_graph.invoke({"messages": state["messages"][-1]})
    return Command(
        update={"messages": [HumanMessage(content=response["messages"][-1].content, name="content_writing_team")]},
        goto="supervisor"
    )

# 1. Create a new StateGraph for the full system
final_graph = StateGraph(State)

# 2. Add Top Supervisor and Subteams as nodes
final_graph.add_node("supervisor", top_supervisor_node)
final_graph.add_node("data_analysis_team", call_data_analysis_team)
final_graph.add_node("content_writing_team", call_content_writing_team)

# 3. Define edges
final_graph.add_edge(START, "supervisor")

# 4. Compile the final graph
compiled_final_graph = final_graph.compile()

user_query = (
    "Here is a list of smartphone sales data: [120, 135, 140, 155, 165]."
    "Analyze it and provide detailed basic statistics (mean, median, mode) "
    "and also identify if there is any sales trend."
)

if __name__ == "__main__":
    # Seed the MessagesState with the user's question
    initial_state = {
        "messages": [
            HumanMessage(content=user_query, name="user")
        ]
    }

    print("Running multi-agent workflow...\n")
    for step in compiled_final_graph.stream(initial_state):
        if 'supervisor' in step:
            print('supervisor',step['supervisor']['next'])
        else:
            for k in step:
                print(k, step[k]['messages'][-1].content)
