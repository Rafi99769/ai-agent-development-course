---
marp: true
theme: default
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.svg')
---

<!-- _class: lead -->

# 🔷 LangGraph Tutorial
## Building Stateful AI Agents with Graphs

**A Complete Guide to Modern Agent Orchestration**

---

# Slide 1: What is LangGraph?

## 🎯 Overview

**LangGraph** is a low-level orchestration framework for building **stateful, multi-actor AI agents** using graph structures.

### Key Features:
- ✅ **Durable Execution** - Agents persist through failures
- ✅ **Human-in-the-Loop** - Inspect and modify agent state
- ✅ **Comprehensive Memory** - Short & long-term memory
- ✅ **Production-Ready** - Scalable deployment infrastructure

### Built By:
LangChain Inc. (can be used with or without LangChain)

> *"Agents as graphs, not chains"*

---

# Slide 2: Core Concepts - The Building Blocks

## 🧱 Three Essential Components

### 1. **State** 📦
- Shared data structure representing the current snapshot
- Passed between nodes via edges
- Typically defined using `TypedDict` or Pydantic `BaseModel`

### 2. **Nodes** ⚙️
- Functions that perform the actual work
- Process state and return updated state
- Can execute any logic: LLM calls, computations, API calls

### 3. **Edges** 🔗
- Define the flow between nodes
- Determine "what happens next"
- Can be conditional or fixed

---

# Slide 3: Understanding State

## 📦 State: The Communication Backbone

### What is State?
State is a **shared data structure** that represents your application's current snapshot at any moment.

### Example State Schema:
```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict
    context: str
```

### Key Points:
- State carries output from one node as input to the next
- Schema ensures consistent data format
- Annotated types enable **reducers** (e.g., `add_messages` appends instead of replaces)

---

# Slide 4: Nodes - Where Work Happens

## ⚙️ Nodes: The Workhorses

### Node Definition:
Nodes are **Python functions** that take state as input and return updated state.

```python
def my_node(state: AgentState):
    # Process the state
    messages = state["messages"]
    
    # Do some work (LLM call, computation, etc.)
    response = llm.invoke(messages)
    
    # Return updated state
    return {"messages": [response]}
```

### Node Characteristics:
- ✅ Can contain any Python logic
- ✅ Must accept state as input
- ✅ Must return dict with state updates
- ✅ Updates are merged with existing state

---

# Slide 5: Edges - Defining Flow

## 🔗 Edges: The Routing Logic

### Two Types of Edges:

#### 1. **Normal Edges** (Fixed Flow)
```python
graph.add_edge("node_a", "node_b")  # Always goes to node_b
graph.add_edge(START, "node_a")      # Entry point
graph.add_edge("node_b", END)        # Exit point
```

#### 2. **Conditional Edges** (Dynamic Routing)
```python
def router(state: AgentState) -> str:
    if state["needs_tool"]:
        return "tool_node"
    return END

graph.add_conditional_edges("agent", router)
```

### Special Nodes:
- **START**: Entry point to the graph
- **END**: Exit point from the graph

---

# Slide 6: Building Your First Graph

## 🏗️ Step-by-Step Construction

```python
from langgraph.graph import StateGraph, MessagesState, START, END

# Step 1: Define your node function
def chatbot(state: MessagesState):
    return {"messages": [llm.invoke(state["messages"])]}

# Step 2: Create the graph
graph = StateGraph(MessagesState)

# Step 3: Add nodes
graph.add_node("chatbot", chatbot)

# Step 4: Add edges
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# Step 5: Compile
app = graph.compile()

# Step 6: Run
result = app.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
```

---

# Slide 7: Real-World Example - Agent with Tools

## 🛠️ Building a Tool-Calling Agent

```python
from langgraph.prebuilt import ToolNode

# Define tools
@tool
def calculator(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

tools = [calculator]
llm_with_tools = llm.bind_tools(tools)

# Agent node - decides to use tools or respond
def agent(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Router - check if tools are needed
def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", agent)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")  # Loop back after tool use
app = workflow.compile()
```

---

# Slide 8: Advanced Features

## 🚀 Power Features for Production

### 1. **Persistence & Checkpointing**
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Resume from checkpoint
app.invoke(input, config={"configurable": {"thread_id": "1"}})
```

### 2. **Human-in-the-Loop**
```python
# Add interrupts
app = workflow.compile(interrupt_before=["sensitive_action"])

# Get state, modify, continue
state = app.get_state(config)
app.update_state(config, modified_state)
```

### 3. **Streaming**
```python
for chunk in app.stream(input):
    print(chunk)
```

---

# Slide 9: Graph Visualization & Debugging

## 🔍 Understanding Your Agent Flow

### Visualize the Graph:
```python
from IPython.display import Image, display

# Generate graph diagram
display(Image(app.get_graph().draw_mermaid_png()))
```

### Example Flow Diagram:
```
    START
      ↓
   ┌──────┐
   │ Agent│ ← Decides what to do
   └──┬───┘
      ↓
   Decision?
   ├─→ Tools → (loops back to Agent)
   └─→ END
```

### Debugging with LangSmith:
- Trace execution paths
- Inspect state at each step
- Monitor performance metrics
- Visualize agent behavior

---

# Slide 10: Best Practices & Next Steps

## ✨ Tips for Success

### Best Practices:
1. **Keep Nodes Simple** - One responsibility per node
2. **Use Reducers** - For list/dict merging (e.g., `add_messages`)
3. **Handle Errors** - Add error handling nodes
4. **Test Incrementally** - Build and test node by node
5. **Log State Changes** - Monitor state evolution

### Common Patterns:
- 🔄 **ReAct Agent**: Agent → Tool → Agent (loop)
- 🤝 **Multi-Agent**: Parallel agents collaborating
- 👥 **Human-in-Loop**: Pause for human approval
- 💾 **Memory**: Persist conversations across sessions

### Next Steps:
- 📚 [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- 🎓 [LangChain Academy](https://academy.langchain.com/)
- 💻 Build your first agent today!

---

<!-- _class: lead -->

# 🎉 Thank You!

## Ready to Build Stateful Agents?

**Resources:**
- 📖 Docs: https://docs.langchain.com/oss/python/langgraph/
- 💬 Community: https://github.com/langchain-ai/langgraph
- 🚀 Deploy: LangSmith Platform

**Questions?**

*Start building graphs, not chains!*
