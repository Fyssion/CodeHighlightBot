import datetime


class Code:
    __slots__ = ("code", "language", "message_id", "chat_id", "user_id", "created_at")

    def __init__(self, code, language, message_id, chat_id, user_id):
        self.code = code
        self.language = language
        self.message_id = message_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.created_at = datetime.datetime.utcnow()
