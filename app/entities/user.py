class User:
    def __init__(self, id, first_name, last_name, username):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id
