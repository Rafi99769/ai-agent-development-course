# Module 4 - Class 4: Agent Communication Protocols & Development Frameworks

## MCP, A2A, and ADK

---

## 📋 Agenda

1. **Model Context Protocol (MCP)** - Agent-to-Tool Communication
2. **Agent2Agent Protocol (A2A)** - Agent-to-Agent Communication  
3. **Agent Development Kit (ADK)** - Building Multi-Agent Systems
4. **How They Work Together**
5. **When to Use Each**

---

## Part 1: Model Context Protocol (MCP)

### What is MCP?

**MCP (Model Context Protocol)** is an open-source standard for connecting AI applications to external systems.

> Think of MCP like a **USB-C port for AI applications**

- Standardizes how AI models connect to data sources, tools, and workflows
- Developed by Anthropic and now an open standard
- Enables AI applications to access external information and perform tasks

---

## MCP: Core Concepts

### Architecture Components

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   AI App    │ ◄─MCP──►│ MCP Server  │ ◄──────►│  External   │
│  (Claude)   │         │             │         │   System    │
└─────────────┘         └─────────────┘         └─────────────┘
```

**Three Key Components:**

1. **MCP Host** - AI application (Claude, ChatGPT, etc.)
2. **MCP Server** - Middleware that exposes capabilities
3. **External Systems** - Data sources, tools, APIs

---

## MCP: How It Works

### Communication Flow

1. **Discovery**: AI application discovers available MCP servers
2. **Connection**: Establishes connection using standardized protocol
3. **Tool Registration**: MCP server exposes tools, resources, and prompts
4. **Invocation**: AI model calls tools through MCP interface
5. **Response**: MCP server returns results to AI application

### Key Features

- **Resources**: Access to data sources (files, databases, APIs)
- **Tools**: Executable functions (search, calculate, transform)
- **Prompts**: Specialized prompt templates for specific tasks

---

## MCP: Use Cases

### When to Use MCP

✅ **Connecting AI to external data sources**
- Local files, databases, cloud storage
- Enterprise data systems

✅ **Extending AI capabilities with tools**
- Search engines, calculators, APIs
- Custom business logic

✅ **Building AI assistants with context**
- Personal assistants (Calendar, Notion, Email)
- Enterprise chatbots with organizational data

### Example Applications

- Claude accessing Google Calendar and Notion
- AI generating web apps from Figma designs
- Enterprise chatbots querying multiple databases
- AI controlling 3D printers and IoT devices

---

## Part 2: Agent2Agent Protocol (A2A)

### What is A2A?

**A2A (Agent2Agent Protocol)** is an open standard for enabling communication and collaboration between AI agents.

> A2A acts as the **public internet for AI agents**

- Originally developed by Google, now under Linux Foundation
- Enables agents from different frameworks to communicate
- Supports secure, opaque agent interactions

---

## A2A: Core Concepts

### Architecture Overview

```
┌──────────────┐                    ┌──────────────┐
│ Client Agent │ ◄────── A2A ──────►│ Remote Agent │
│  (Any Frame) │                    │  (Any Frame) │
└──────────────┘                    └──────────────┘
       │                                    │
       │ A2A                           A2A  │
       ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│ Remote Agent │                    │ Remote Agent │
│      2       │                    │      3       │
└──────────────┘                    └──────────────┘
```

**Key Principles:**

- **Interoperability**: Connect agents across different platforms
- **Decentralized**: No central authority required
- **Secure**: Agents don't share internal memory or tools
- **Opaque**: Preserves intellectual property

---

## A2A: How It Works

### Communication Protocol

**1. Agent Discovery**
- Agents advertise their capabilities
- Discovery can be dynamic or pre-configured

**2. Task Delegation**
- Client agent sends task request to remote agent
- Includes context, parameters, and expected output format

**3. Execution & Response**
- Remote agent processes task independently
- Returns results without exposing internal logic

**4. Coordination**
- Multiple agents can collaborate on complex workflows
- Supports parallel and sequential execution

---

## A2A: Protocol Features

### Message Structure

```json
{
  "task": "analyze_sentiment",
  "input": "User feedback text...",
  "context": {
    "language": "en",
    "domain": "customer_service"
  },
  "response_format": "structured"
}
```

### Security Features

- **Authentication**: OAuth 2.0, OpenID Connect support
- **Authorization**: Fine-grained access control
- **Encryption**: Secure transport layer
- **Privacy**: No internal state sharing

---

## A2A: Use Cases

### When to Use A2A

✅ **Multi-agent systems**
- Agents need to collaborate on complex tasks
- Delegation of specialized sub-tasks

✅ **Cross-platform agent communication**
- Agents built with different frameworks (LangGraph, CrewAI, etc.)
- Enterprise systems with heterogeneous agents

✅ **Secure agent collaboration**
- Preserving proprietary logic and IP
- Enterprise environments with security requirements

### Example Applications

- Research agent delegating to specialized analysis agents
- Customer service routing to domain-specific agents
- Multi-vendor agent ecosystems
- Enterprise agent orchestration

---

## Part 3: Agent Development Kit (ADK)

### What is ADK?

**ADK (Agent Development Kit)** is Google's open-source framework for building and deploying AI agents.

> Makes agent development feel like **software development**

- Model-agnostic (optimized for Gemini, works with others)
- Deployment-agnostic (Cloud Run, Vertex AI, Docker)
- Framework-compatible (integrates with existing tools)

---

## ADK: Core Concepts

### Agent Types

**1. LLM Agents**
- Dynamic, LLM-driven decision making
- Adaptive behavior based on context

**2. Workflow Agents**
- Predictable, structured pipelines
- Sequential, Parallel, or Loop execution

**3. Custom Agents**
- Specialized capabilities
- Unique integrations and rules

---

## ADK: Architecture

### Multi-Agent System Design

```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
│  (Coordinates overall workflow)         │
└────────┬──────────────┬─────────────────┘
         │              │
    ┌────▼────┐    ┌────▼────┐    ┌──────────┐
    │ Agent 1 │    │ Agent 2 │    │ Agent 3  │
    │Research │    │Analysis │    │ Report   │
    └────┬────┘    └────┬────┘    └────┬─────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼─────┐
    │ Tools   │    │ Tools   │    │ Tools    │
    └─────────┘    └─────────┘    └──────────┘
```

---

## ADK: Key Features

### 1. Flexible Orchestration

**Workflow Agents:**
```python
from google.adk import Sequential, Parallel, Loop

# Sequential workflow
workflow = Sequential([
    research_agent,
    analysis_agent,
    report_agent
])

# Parallel execution
parallel_workflow = Parallel([
    web_search_agent,
    database_query_agent,
    api_call_agent
])
```

---

## ADK: Key Features (Continued)

### 2. Rich Tool Ecosystem

**Built-in Tools:**
- Search (web, knowledge bases)
- Code execution
- Data processing

**Custom Tools:**
- Function-based tools
- Third-party integrations
- Other agents as tools

**Tool Example:**
```python
@tool
def calculate_roi(investment: float, return_value: float) -> float:
    """Calculate return on investment"""
    return ((return_value - investment) / investment) * 100
```

---

## ADK: Key Features (Continued)

### 3. Deployment Ready

**Deployment Options:**
- **Local Development**: Run on your machine
- **Cloud Run**: Containerized deployment
- **Vertex AI Agent Engine**: Scalable managed service
- **Custom Infrastructure**: Docker, Kubernetes

**One-Command Deploy:**
```bash
adk deploy --platform vertex-ai
```

---

## ADK: Key Features (Continued)

### 4. Built-in Evaluation

**Evaluation Framework:**
- Test agent responses against expected outputs
- Evaluate step-by-step execution trajectory
- Systematic performance assessment

```python
from google.adk import evaluate

results = evaluate(
    agent=my_agent,
    test_cases=[
        {"input": "...", "expected": "..."},
        {"input": "...", "expected": "..."}
    ]
)
```

---

## ADK: Use Cases

### When to Use ADK

✅ **Building production-ready agents**
- Need deployment flexibility
- Require evaluation and testing

✅ **Multi-agent architectures**
- Complex workflows with multiple specialized agents
- Hierarchical agent systems

✅ **Google Cloud integration**
- Using Gemini models
- Deploying on Vertex AI or Cloud Run

✅ **Code-first development**
- Prefer programmatic control
- Software engineering best practices

---

## Part 4: How They Work Together

### The Complete Stack

```
┌─────────────────────────────────────────────────────┐
│                    User / Application                │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   Agent (Built with   │
         │        ADK)           │
         └───────┬───────┬───────┘
                 │       │
         ┌───────▼───┐   └───────▼──────┐
         │    MCP    │           │  A2A  │
         │ (Tools &  │           │(Agent │
         │Resources) │           │ Comm) │
         └───────┬───┘           └───┬───┘
                 │                   │
         ┌───────▼────────┐   ┌──────▼──────┐
         │ External Tools │   │Other Agents │
         │  & Data        │   │             │
         └────────────────┘   └─────────────┘
```

---

## How They Work Together (Continued)

### Integration Example

**Scenario: Research Assistant Agent**

1. **Built with ADK**
   - Multi-agent architecture
   - Orchestrator + specialized agents

2. **Uses MCP for tools**
   - Web search via MCP server
   - Database access via MCP server
   - File system access via MCP server

3. **Uses A2A for collaboration**
   - Delegates analysis to specialized agent
   - Communicates with fact-checking agent
   - Coordinates with report generation agent

---

## Comparison Matrix

| Feature | MCP | A2A | ADK |
|---------|-----|-----|-----|
| **Purpose** | Agent↔Tool | Agent↔Agent | Build Agents |
| **Scope** | Tool integration | Agent communication | Development framework |
| **Standardization** | Protocol | Protocol | Framework |
| **Interoperability** | Tool-level | Agent-level | Framework-level |
| **Security** | Tool access control | Agent authentication | Built-in patterns |
| **Deployment** | N/A | N/A | Multi-platform |

---

## When to Use What?

### Decision Framework

**Use MCP when:**
- ✅ Your agent needs to access external tools/data
- ✅ You want standardized tool integration
- ✅ You're building single-agent systems with rich capabilities

**Use A2A when:**
- ✅ You need multiple agents to collaborate
- ✅ Agents are built with different frameworks
- ✅ Security and IP protection are critical
- ✅ You're building agent marketplaces/ecosystems

**Use ADK when:**
- ✅ You're building agents from scratch
- ✅ You need production deployment capabilities
- ✅ You want multi-agent orchestration
- ✅ You're using Google Cloud/Gemini

---

## Real-World Architecture Example

### Enterprise AI Assistant

```
┌─────────────────────────────────────────────────────┐
│          Main Assistant (ADK LLM Agent)             │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
   MCP │          A2A │          A2A │
       │              │              │
┌──────▼─────┐  ┌─────▼──────┐  ┌───▼──────────┐
│ Calendar   │  │ Research   │  │ Data Analysis│
│ MCP Server │  │ Agent      │  │ Agent        │
└────────────┘  └─────┬──────┘  └───┬──────────┘
                      │             │
                  MCP │         MCP │
                      │             │
                ┌─────▼──────┐  ┌───▼──────────┐
                │ Web Search │  │ Database     │
                │ MCP Server │  │ MCP Server   │
                └────────────┘  └──────────────┘
```

---

## Implementation Patterns

### Pattern 1: Single Agent with Tools (MCP)

**Best for:** Simple assistants, chatbots, single-purpose agents

```python
# ADK agent with MCP tools
agent = LlmAgent(
    model="gemini-pro",
    tools=[
        mcp_tool("search"),
        mcp_tool("calendar"),
        mcp_tool("database")
    ]
)
```

---

## Implementation Patterns (Continued)

### Pattern 2: Multi-Agent System (A2A)

**Best for:** Complex workflows, specialized agents, enterprise systems

```python
# Orchestrator agent
orchestrator = LlmAgent(
    model="gemini-pro",
    tools=[
        a2a_agent("research_agent"),
        a2a_agent("analysis_agent"),
        a2a_agent("report_agent")
    ]
)

# Each remote agent can have its own MCP tools
research_agent = LlmAgent(
    model="gemini-pro",
    tools=[
        mcp_tool("web_search"),
        mcp_tool("academic_db")
    ]
)
```

---

## Implementation Patterns (Continued)

### Pattern 3: Hybrid Architecture

**Best for:** Enterprise applications, maximum flexibility

```python
# Main agent with both MCP and A2A
main_agent = LlmAgent(
    model="gemini-pro",
    tools=[
        # Direct MCP tools for common tasks
        mcp_tool("calendar"),
        mcp_tool("email"),
        
        # A2A agents for specialized tasks
        a2a_agent("legal_review_agent"),
        a2a_agent("financial_analysis_agent"),
        a2a_agent("compliance_check_agent")
    ]
)
```

---

## Best Practices

### MCP Best Practices

1. **Design clear tool interfaces**
   - Well-defined input/output schemas
   - Comprehensive documentation

2. **Implement proper error handling**
   - Graceful failures
   - Informative error messages

3. **Optimize for performance**
   - Cache frequently accessed data
   - Minimize latency

4. **Security first**
   - Validate all inputs
   - Implement proper authentication

---

## Best Practices (Continued)

### A2A Best Practices

1. **Define clear agent contracts**
   - Specify capabilities and limitations
   - Document expected inputs/outputs

2. **Implement robust error handling**
   - Handle agent unavailability
   - Timeout management

3. **Design for scalability**
   - Stateless agent design
   - Load balancing considerations

4. **Monitor and observe**
   - Track agent interactions
   - Performance metrics

---

## Best Practices (Continued)

### ADK Best Practices

1. **Modular agent design**
   - Single responsibility principle
   - Reusable components

2. **Comprehensive testing**
   - Unit tests for individual agents
   - Integration tests for workflows
   - Use built-in evaluation framework

3. **Proper orchestration**
   - Choose right workflow type (Sequential, Parallel, Loop)
   - Handle failures gracefully

4. **Production readiness**
   - Implement logging and monitoring
   - Use proper deployment strategies
   - Version control for agents

---

## Getting Started

### Quick Start: MCP

```bash
# Install MCP SDK
pip install mcp

# Create MCP server
from mcp import Server, Tool

server = Server("my-tools")

@server.tool()
def search(query: str) -> str:
    # Implementation
    return results

server.run()
```

---

## Getting Started (Continued)

### Quick Start: A2A

```bash
# Install A2A SDK
pip install a2a-python

# Create A2A agent
from a2a import Agent, Task

agent = Agent("my-agent")

@agent.task()
async def process_task(task: Task):
    # Implementation
    return result

agent.start()
```

---

## Getting Started (Continued)

### Quick Start: ADK

```bash
# Install ADK
pip install google-adk

# Create agent
from google.adk import LlmAgent

agent = LlmAgent(
    model="gemini-pro",
    system_prompt="You are a helpful assistant",
    tools=[...]
)

# Run agent
response = agent.run("What's the weather?")
```

---

## Resources & Documentation

### Official Documentation

**MCP:**
- 🌐 [modelcontextprotocol.io](https://modelcontextprotocol.io)
- 📚 [Introduction Guide](https://modelcontextprotocol.io/introduction)
- 💻 [GitHub](https://github.com/modelcontextprotocol)

**A2A:**
- 🌐 [a2a-protocol.org](https://a2a-protocol.org)
- 📚 [Specification](https://a2a-protocol.org/latest/specification/)
- 💻 [GitHub Samples](https://github.com/a2aproject/a2a-samples)

**ADK:**
- 🌐 [google.github.io/adk-docs](https://google.github.io/adk-docs/)
- 📚 [Get Started Guide](https://google.github.io/adk-docs/get-started/python/)
- 💻 [GitHub](https://github.com/google/adk-python)

---

## Community & Support

### SDKs Available

**A2A Protocol:**
- Python, JavaScript, Java, C#/.NET, Golang

**ADK:**
- Python, Go, Java

**MCP:**
- Python, TypeScript, multiple community implementations

### Community Resources

- Linux Foundation AI & Data
- Google Cloud Community
- Anthropic Developer Community
- GitHub Discussions and Issues

---

## Summary

### Key Takeaways

1. **MCP** = Agent ↔ Tool Communication
   - Standardizes how agents access external resources
   - Like USB-C for AI applications

2. **A2A** = Agent ↔ Agent Communication
   - Enables multi-agent collaboration
   - Like the internet for AI agents

3. **ADK** = Agent Development Framework
   - Build, deploy, and orchestrate agents
   - Production-ready, code-first approach

4. **Together** = Complete AI Agent Ecosystem
   - Build with ADK, equip with MCP, communicate with A2A

---

## Q&A

### Questions?

**Topics covered:**
- ✅ What are MCP, A2A, and ADK
- ✅ How each protocol/framework works
- ✅ When to use each one
- ✅ How they work together
- ✅ Best practices and patterns
- ✅ Getting started resources

---

## Next Steps

### Hands-on Practice

1. **Experiment with MCP**
   - Build a simple MCP server
   - Connect it to an AI application

2. **Try A2A**
   - Create two agents that communicate
   - Implement task delegation

3. **Build with ADK**
   - Create a multi-agent system
   - Deploy to Cloud Run or Vertex AI

4. **Combine all three**
   - Build a complete agent ecosystem
   - Implement real-world use case

---

## Thank You!

### Module 4 - Class 4 Complete
---
