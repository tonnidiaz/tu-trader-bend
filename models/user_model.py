from bunnet import Document, Indexed

class User(Document):
    username: Indexed(str, unique=True)
    io_id: str = ""