class ConversationMemory:
    def __init__(self):
        self.messages = []
        
    def add_user_message(self, message: str):
        self.messages.append({"role": "user", "content": message})
        
    def add_assistant_message(self, message: str):
        self.messages.append({"role": "assistant", "content": message})
        
    def get_context_string(self, n_recent=5) -> str:
        """Returns the last N messages as a formatted string."""
        recent_messages = self.messages[-n_recent:]
        context = ""
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        return context
