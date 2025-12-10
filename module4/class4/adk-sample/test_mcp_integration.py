"""
Test script to verify MCP server integration with main agent
"""
import asyncio
from main_agent.agent import root_agent


async def test_agent():
    """Test the agent with MCP time tool"""
    print("Testing agent with MCP time tool integration...\n")
    
    # Test 1: Ask for current time
    print("Test 1: Asking for current time in UTC")
    response = await root_agent.run_async("What is the current time?")
    print(f"Response: {response}\n")
    
    # Test 2: Ask for time in a specific timezone
    print("Test 2: Asking for current time in New York")
    response = await root_agent.run_async("What is the current time in New York?")
    print(f"Response: {response}\n")
    
    # Test 3: Test the joke function still works
    print("Test 3: Testing joke function")
    response = await root_agent.run_async("Tell me a joke")
    print(f"Response: {response}\n")


if __name__ == "__main__":
    asyncio.run(test_agent())
