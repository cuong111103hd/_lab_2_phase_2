import os
from langchain_core.messages import HumanMessage
from src.agent.graph import MultiMemoryAgent
from dotenv import load_dotenv

load_dotenv()

def main():
    agent = MultiMemoryAgent()
    state = {
        "messages": [],
        "user_profile": "",
        "episodes": [],
        "semantic_hits": [],
        "memory_budget": 1500
    }

    print("--- Multi-Memory Agent Interactive Demo ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        state["messages"].append(HumanMessage(content=user_input))
        
        # Run agent
        state = agent.invoke(state)
        
        # Get AI response
        ai_response = state["messages"][-1].content
        print(f"\nAgent: {ai_response}")
        
        # Update memory backends
        agent.router.update_memory(state)

if __name__ == "__main__":
    main()
