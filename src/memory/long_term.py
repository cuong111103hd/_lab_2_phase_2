import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LongTermMemory:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.profile_key = "user_profile"

    def update_profile(self, key: str, value: str):
        """Update a specific fact in the user profile."""
        profile = self.get_profile()
        profile[key] = value
        self.client.set(self.profile_key, json.dumps(profile))

    def get_profile(self) -> dict:
        """Retrieve the entire user profile."""
        data = self.client.get(self.profile_key)
        if data:
            return json.loads(data)
        return {}

    def get_formatted_profile(self) -> str:
        """Get profile as a formatted string for prompt injection."""
        profile = self.get_profile()
        if not profile:
            return "No profile facts known yet."
        
        formatted = ""
        for k, v in profile.items():
            formatted += f"- {k}: {v}\n"
        return formatted

    def clear(self):
        self.client.delete(self.profile_key)
