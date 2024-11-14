class Group:
    def __init__(self, id, title, name, is_channel, is_group, is_user, read_inbox_max_id, read_outbox_max_id,
                 top_message, unread_count, archived, creation_date):
        self.id = id
        self.title = title
        self.name = name
        self.is_channel = is_channel
        self.is_group = is_group
        self.is_user = is_user
        self.read_inbox_max_id = read_inbox_max_id
        self.read_outbox_max_id = read_outbox_max_id
        self.top_message = top_message
        self.unread_count = unread_count
        self.archived = archived
        self.creation_date = creation_date

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id