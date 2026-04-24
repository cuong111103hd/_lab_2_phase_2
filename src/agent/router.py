import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

from src.memory.short_term import ShortTermMemory
from src.memory.long_term import LongTermMemory
from src.memory.episodic import EpisodicMemory
from src.memory.semantic import SemanticMemory
from src.utils.llm import trim_memory

load_dotenv()

class MemoryRouter:
    def __init__(self):
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.llm = ChatOpenAI(temperature=0, model=model_name)
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()

    def route_query(self, query: str) -> dict:
        """
        Determine the intent of the query and fetch relevant memory.
        Returns a dict of memory pieces.
        """
        # Very simple routing using LLM to classify intent
        prompt = f"""
        Analyze the following query and decide which types of memory are needed to answer it.
        Return JSON format with boolean flags:
        {{
            "needs_profile": true/false, (if query relates to user's personal facts, preferences)
            "needs_episodes": true/false, (if query asks about past interactions, previous tasks)
            "needs_semantic": true/false (if query asks for general knowledge, facts)
        }}
        Query: {query}
        """
        try:
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            intent = json.loads(resp.content.strip().replace("```json", "").replace("```", ""))
        except Exception:
            intent = {"needs_profile": True, "needs_episodes": True, "needs_semantic": True}

        memory_pieces = {
            "profile": self.long_term.get_formatted_profile() if intent.get("needs_profile") else "",
            "episodes": self.episodic.get_formatted_episodes() if intent.get("needs_episodes") else "",
            "semantic": self.semantic.search_knowledge(query) if intent.get("needs_semantic") else ""
        }
        return memory_pieces

    def retrieve_memory(self, state: dict) -> dict:
        """
        Node function to retrieve memory and populate state.
        """
        # Get latest query
        latest_query = state["messages"][-1].content if state["messages"] else ""
        
        memories = self.route_query(latest_query)
        
        # We don't overwrite messages here, just update the context
        return {
            "user_profile": memories["profile"],
            "episodes": [{"content": memories["episodes"]}] if memories["episodes"] and memories["episodes"] != "No previous episodes." else [],
            "semantic_hits": [memories["semantic"]] if memories["semantic"] else []
        }

    def update_memory(self, state: dict) -> dict:
        """
        Node function to update memories after agent response.
        """
        messages = state["messages"]
        if len(messages) < 2:
            return {}
            
        user_input = messages[-2].content
        ai_output = messages[-1].content
        
        # 1. Update Short Term
        self.short_term.save_context(user_input, ai_output)
        
        # 2. Update Long Term (Profile) and Episodic
        update_prompt = f"""
        Based on this recent interaction, extract any facts about the user to update their profile, 
        and summarize the interaction as an episode if it's a completed task.
        
        Return JSON format:
        {{
            "profile_updates": {{"fact_key": "fact_value"}}, (e.g. {{"allergy": "peanuts"}}. If user corrects a fact, use the new value)
            "new_episode": {{"task": "...", "outcome": "...", "learnings": "..."}} (or null if not a significant episode)
        }}
        
        User: {user_input}
        AI: {ai_output}
        """
        try:
            resp = self.llm.invoke([SystemMessage(content="You are a memory extractor."), HumanMessage(content=update_prompt)])
            updates = json.loads(resp.content.strip().replace("```json", "").replace("```", ""))
            
            if updates.get("profile_updates"):
                for k, v in updates["profile_updates"].items():
                    self.long_term.update_profile(k, v)
                    
            if updates.get("new_episode"):
                self.episodic.save_episode(updates["new_episode"])
        except Exception as e:
            pass
            
        return {}
