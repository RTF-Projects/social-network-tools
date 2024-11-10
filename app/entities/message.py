class Message:
    def __init__(self, id, date, chat_id, from_id, message):
        self.id = id
        self.date = date
        self.chat_id = chat_id
        self.from_id = from_id
        self.message = message