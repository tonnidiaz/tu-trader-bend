from typing import Optional
from bunnet import Document, Indexed, PydanticObjectId

class User(Document):
    username: Indexed(str, unique=True)
    email: Indexed(str, unique=True)
    password: Indexed(str, unique=True)
    io_id: str = ""
    new_email: str = ""
    otp: Optional[int]
    is_admin: bool = False
    is_verified: bool = False
    apps: list[PydanticObjectId] = []