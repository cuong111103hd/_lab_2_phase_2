from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

from src.agent.state import MemoryState
from src.agent.router import MemoryRouter
from src.utils.llm import trim_memory

load_dotenv()

class MultiMemoryAgent:
    def __init__(self, memory_budget: int = 1500):
        self.router = MemoryRouter()
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.llm = ChatOpenAI(temperature=0.7, model=model_name)
        self.memory_budget = memory_budget
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(MemoryState)

        # Nodes
        workflow.add_node("retrieve", self.router.retrieve_memory)
        workflow.add_node("trim", self._trim_node)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("update", self.router.update_memory)

        # Edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "trim")
        workflow.add_edge("trim", "agent")
        workflow.add_edge("agent", "update")
        workflow.add_edge("update", END)

        return workflow.compile()

    def _trim_node(self, state: MemoryState):
        state["memory_budget"] = self.memory_budget
        return trim_memory(state, self.memory_budget)

    def _agent_node(self, state: MemoryState):
        # Build prompt with injected memory
        system_prompt = f"""
You are a helpful AI assistant with a multi-tiered memory system.

--- User Profile (Long-term Memory) ---
{state.get('user_profile', 'No profile facts known yet.')}

--- Relevant Past Episodes (Episodic Memory) ---
{chr(10).join([str(ep) for ep in state.get('episodes', [])]) if state.get('episodes') else 'No previous episodes.'}

--- Relevant Knowledge (Semantic Memory) ---
{chr(10).join(state.get('semantic_hits', [])) if state.get('semantic_hits') else 'No semantic knowledge retrieved.'}
---

Use the above context to answer the user's latest query. If the user corrects a previous fact (e.g., changing their allergy), acknowledge it.
"""
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def invoke(self, state: dict):
        return self.graph.invoke(state)
