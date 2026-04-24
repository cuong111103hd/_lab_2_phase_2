import json
import os

class EpisodicMemory:
    def __init__(self, log_file="data/episodes.json"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def save_episode(self, episode: dict):
        """Save a new episode (e.g., {'task': ..., 'outcome': ..., 'learnings': ...})."""
        episodes = self.get_all_episodes()
        episodes.append(episode)
        with open(self.log_file, "w") as f:
            json.dump(episodes, f, indent=4)

    def get_all_episodes(self) -> list:
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def get_formatted_episodes(self) -> str:
        episodes = self.get_all_episodes()
        if not episodes:
            return "No previous episodes."
        
        formatted = ""
        for i, ep in enumerate(episodes[-5:]): # Only return last 5 for context
            formatted += f"Episode {i+1}:\n"
            for k, v in ep.items():
                formatted += f"  - {k}: {v}\n"
        return formatted

    def clear(self):
        with open(self.log_file, "w") as f:
            json.dump([], f)
