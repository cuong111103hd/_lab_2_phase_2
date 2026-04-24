import tiktoken

def get_token_count(text: str, model_name: str = "gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def trim_memory(state: dict, budget: int) -> dict:
    """
    Priority-based eviction with 4-level hierarchy:
    Level 1: System Prompt / Profile (Highest - NEVER trim)
    Level 2: Semantic Hits (Knowledge)
    Level 3: Episodic Memories (Past experiences)
    Level 4: Recent Conversation History (Short-term - Lowest)
    
    Trimming starts from Level 4 up to Level 2.
    """
    # Level 1: Profile
    profile_text = state.get("user_profile", "")
    l1_tokens = get_token_count(profile_text)
    
    # Level 2: Semantic
    semantic_hits = state.get("semantic_hits", [])
    # Level 3: Episodes
    episodes = state.get("episodes", [])
    # Level 4: Messages
    messages = state.get("messages", [])

    # Start trimming from Level 4 (Messages)
    while True:
        l2_text = "\n".join(semantic_hits)
        l3_text = "\n".join([str(ep) for ep in episodes])
        l4_text = "\n".join([msg.content for msg in messages])
        
        total = l1_tokens + get_token_count(l2_text) + get_token_count(l3_text) + get_token_count(l4_text)
        
        if total <= budget:
            break
            
        # 1. Trim Level 4
        if messages:
            messages.pop(0)
            continue
            
        # 2. Trim Level 3
        if episodes:
            episodes.pop(0)
            continue
            
        # 3. Trim Level 2
        if semantic_hits:
            semantic_hits.pop(0)
            continue
            
        # Level 1 is never trimmed
        break

    state["messages"] = messages
    state["episodes"] = episodes
    state["semantic_hits"] = semantic_hits
    return state
