from typing import TypedDict, Annotated, List, Dict
from langchain_core.messages import BaseMessage
import operator

class MemoryState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_profile: str
    episodes: List[Dict]
    semantic_hits: List[str]
    memory_budget: int
