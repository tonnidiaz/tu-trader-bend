from typing import Optional
from bunnet import Document, Indexed

from models.app_model import App

class User(Document):
    email: Indexed(str, unique=True)
    password: Indexed(str, unique=True)
    io_id: str = ""
    new_email: str = ""
    otp: Optional[int]
    is_admin: bool = False
    is_verified: bool = False
    app: list[App] = []