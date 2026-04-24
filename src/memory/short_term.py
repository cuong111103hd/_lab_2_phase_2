class ShortTermMemory:
    def __init__(self):
        self.messages = []

    def save_context(self, user_input: str, ai_output: str):
        self.messages.append({"role": "User", "content": user_input})
        self.messages.append({"role": "Agent", "content": ai_output})

    def load_memory_variables(self) -> str:
        # Keep last 10 messages for safety
        history = ""
        for msg in self.messages[-10:]:
            history += f"{msg['role']}: {msg['content']}\n"
        return history

    def clear(self):
        self.messages = []
