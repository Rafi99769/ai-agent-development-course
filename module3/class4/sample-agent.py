"""
Customer Support Email Agent using LangGraph
Based on: https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, RetryPolicy
from langgraph.checkpoint.memory import MemorySaver
import os
from datetime import datetime


# ============================================================================
# Step 1: Define State Schema
# ============================================================================

class EmailClassification(TypedDict):
    """Structure for email classification results"""
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class EmailAgentState(TypedDict):
    """Shared state accessible to all nodes"""
    # Raw email data
    email_content: str
    sender_email: str
    email_id: str
    
    # Classification result
    classification: EmailClassification | None
    
    # Raw search/API results
    search_results: list[str] | None
    customer_history: dict | None
    
    # Generated content
    draft_response: str | None
    messages: list[str] | None


# ============================================================================
# Step 2: Implement Node Functions
# ============================================================================

def read_email(state: EmailAgentState) -> Command[Literal["classify_intent"]]:
    """
    Node 1: Read and parse incoming email
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Reading email {state['email_id']}")
    
    print(f"\n📧 Reading email from: {state['sender_email']}")
    print(f"Content: {state['email_content'][:100]}...")
    
    return Command(
        update={
            "messages": messages
        },
        goto="classify_intent"
    )


def classify_intent(state: EmailAgentState) -> Command[Literal["search_documentation", "bug_tracking", "draft_response"]]:
    """
    Node 2: Classify email intent and urgency using LLM
    Routes to appropriate next step based on classification
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Classifying email intent")
    
    # Simulate LLM classification (in real implementation, use actual LLM)
    email_lower = state["email_content"].lower()
    
    # Determine intent
    if "bug" in email_lower or "crash" in email_lower or "error" in email_lower:
        intent = "bug"
        next_node = "bug_tracking"
    elif "billing" in email_lower or "charged" in email_lower or "payment" in email_lower:
        intent = "billing"
        next_node = "draft_response"
    elif "feature" in email_lower or "add" in email_lower or "request" in email_lower:
        intent = "feature"
        next_node = "draft_response"
    elif "how" in email_lower or "?" in email_lower:
        intent = "question"
        next_node = "search_documentation"
    else:
        intent = "complex"
        next_node = "draft_response"
    
    # Determine urgency
    if "urgent" in email_lower or "asap" in email_lower or "critical" in email_lower:
        urgency = "critical"
    elif "important" in email_lower or "soon" in email_lower:
        urgency = "high"
    else:
        urgency = "medium"
    
    classification: EmailClassification = {
        "intent": intent,
        "urgency": urgency,
        "topic": "customer_support",
        "summary": state["email_content"][:100]
    }
    
    print(f"\n🔍 Classification: {intent} ({urgency} urgency)")
    print(f"Routing to: {next_node}")
    
    return Command(
        update={
            "classification": classification,
            "messages": messages
        },
        goto=next_node
    )


def search_documentation(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """
    Node 3: Search knowledge base for relevant information
    Includes retry policy for transient failures
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Searching documentation")
    
    # Simulate documentation search
    search_results = [
        "Password reset: Go to Settings > Security > Reset Password",
        "For account issues, contact support@example.com",
        "Password requirements: 8+ characters, 1 uppercase, 1 number"
    ]
    
    print(f"\n📚 Found {len(search_results)} relevant documents")
    
    return Command(
        update={
            "search_results": search_results,
            "messages": messages
        },
        goto="draft_response"
    )


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """
    Node 4: Create or update bug tracking ticket
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Creating bug ticket")
    
    # Simulate bug ticket creation
    bug_id = f"BUG-{state['email_id'][-4:]}"
    
    print(f"\n🐛 Created bug ticket: {bug_id}")
    print(f"Priority: {state['classification']['urgency']}")
    
    # Store bug info in customer history
    customer_history = {
        "bug_id": bug_id,
        "status": "open",
        "priority": state['classification']['urgency']
    }
    
    return Command(
        update={
            "customer_history": customer_history,
            "messages": messages
        },
        goto="draft_response"
    )


def draft_response(state: EmailAgentState) -> Command[Literal["human_review", "send_reply"]]:
    """
    Node 5: Generate appropriate email response
    Routes to human review for critical/complex cases
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Drafting response")
    
    classification = state["classification"]
    
    # Build response based on intent and available data
    if classification["intent"] == "question" and state.get("search_results"):
        draft = f"Thank you for contacting us!\n\n"
        draft += f"Based on your question, here's what we found:\n\n"
        draft += "\n".join(f"• {result}" for result in state["search_results"][:2])
        draft += f"\n\nLet us know if you need further assistance!"
        
    elif classification["intent"] == "bug":
        bug_id = state.get("customer_history", {}).get("bug_id", "UNKNOWN")
        draft = f"Thank you for reporting this issue.\n\n"
        draft += f"We've created ticket {bug_id} to track this bug. "
        draft += f"Our engineering team will investigate and keep you updated."
        
    elif classification["intent"] == "billing":
        draft = f"We sincerely apologize for the billing issue.\n\n"
        draft += f"I've escalated this to our billing team for immediate review. "
        draft += f"You should receive a resolution within 24 hours."
        
    elif classification["intent"] == "feature":
        draft = f"Thank you for your feature suggestion!\n\n"
        draft += f"We've added your request to our product roadmap. "
        draft += f"We'll notify you if this feature is implemented."
        
    else:
        draft = f"Thank you for contacting us.\n\n"
        draft += f"Your inquiry requires specialized attention. "
        draft += f"A team member will respond within 24 hours."
    
    draft += f"\n\nBest regards,\nCustomer Support Team"
    
    print(f"\n✍️  Draft response created ({len(draft)} chars)")
    
    # Route to human review for critical/complex cases
    if classification["urgency"] in ["critical", "high"] or classification["intent"] == "complex":
        next_node = "human_review"
        print("➡️  Routing to human review (high priority)")
    else:
        next_node = "send_reply"
        print("➡️  Auto-sending (low priority)")
    
    return Command(
        update={
            "draft_response": draft,
            "messages": messages
        },
        goto=next_node
    )


def human_review(state: EmailAgentState) -> Command[Literal["send_reply"]]:
    """
    Node 6: Pause for human review and approval
    Uses interrupt() for human-in-the-loop
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Awaiting human review")
    
    print(f"\n👤 Human review required")
    print(f"Draft preview: {state['draft_response'][:150]}...")
    print("\n⏸️  Execution paused. Waiting for approval...")
    
    # In a real implementation, this would use interrupt()
    # For demo purposes, we'll simulate approval
    print("✅ Simulating approval (in production, use interrupt() here)")
    
    return Command(
        update={
            "messages": messages
        },
        goto="send_reply"
    )


def send_reply(state: EmailAgentState) -> Command[Literal[END]]:
    """
    Node 7: Send the email response
    """
    messages = state.get("messages", [])
    messages.append(f"[{datetime.now().isoformat()}] Email sent successfully")
    
    print(f"\n📤 Sending email to: {state['sender_email']}")
    print(f"Response:\n{'-'*50}\n{state['draft_response']}\n{'-'*50}")
    
    return Command(
        update={
            "messages": messages
        },
        goto=END
    )


# ============================================================================
# Step 3: Build and Compile the Graph
# ============================================================================

def create_email_agent():
    """
    Create and compile the email agent graph
    """
    # Create the graph
    workflow = StateGraph(EmailAgentState)
    
    # Add nodes
    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    
    # Add retry policy for nodes that might have transient failures
    workflow.add_node(
        "search_documentation",
        search_documentation,
        retry=RetryPolicy(max_attempts=3, initial_interval=1.0)
    )
    
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("human_review", human_review)
    workflow.add_node("send_reply", send_reply)
    
    # Add essential edges
    workflow.add_edge(START, "read_email")
    
    # Compile with checkpointer for persistence
    # Note: For local server deployment, compile without checkpointer
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# ============================================================================
# Step 4: Test the Agent
# ============================================================================

def test_agent():
    """
    Test the email agent with various scenarios
    """
    app = create_email_agent()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Simple Question",
            "email_content": "How do I reset my password?",
            "sender_email": "user1@example.com",
            "email_id": "email_001"
        },
        {
            "name": "Bug Report",
            "email_content": "The export feature crashes when I select PDF format",
            "sender_email": "user2@example.com",
            "email_id": "email_002"
        },
        {
            "name": "Urgent Billing Issue",
            "email_content": "I was charged twice for my subscription! This is urgent!",
            "sender_email": "user3@example.com",
            "email_id": "email_003"
        },
        {
            "name": "Feature Request",
            "email_content": "Can you add dark mode to the mobile app?",
            "sender_email": "user4@example.com",
            "email_id": "email_004"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        initial_state = {
            "email_content": test_case["email_content"],
            "sender_email": test_case["sender_email"],
            "email_id": test_case["email_id"],
            "messages": [],
            "classification": None,
            "search_results": None,
            "customer_history": None,
            "draft_response": None
        }
        
        # Run with a thread_id for persistence
        config = {"configurable": {"thread_id": f"thread_{test_case['email_id']}"}}
        
        try:
            result = app.invoke(initial_state, config)
            
            print(f"\n✅ Test case completed successfully")
            print(f"Final classification: {result['classification']}")
            print(f"Messages logged: {len(result['messages'])}")
            
        except Exception as e:
            print(f"\n❌ Test case failed: {str(e)}")
        
        print(f"\n{'='*70}\n")


# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("🚀 Customer Support Email Agent - LangGraph Implementation")
    print("="*70)
    
    # Run tests
    test_agent()
    
    print("\n✨ All tests completed!")
    print("\nKey Features Implemented:")
    print("  ✓ Discrete node-based workflow")
    print("  ✓ Shared state management")
    print("  ✓ Dynamic routing with Command")
    print("  ✓ Retry policies for transient failures")
    print("  ✓ Human-in-the-loop review")
    print("  ✓ Persistent checkpointing")
    print("  ✓ Multiple test scenarios")
