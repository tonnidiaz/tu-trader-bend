import json
from flask import Blueprint, request

from classes.binance import Binance
from models.user_model import User

router = Blueprint('auth', __name__)

@router.post('/auth/signup')
def login_route():
    body = request.json
    username = body.get('username')
    if not username:
        return {'msg': 'Need to provide username'}, 400
    if User.find_one(User.username == username).run():
        return {'msg': 'User already exists'}, 400
    
    user = User(username=username)
    user.save()
    return "Auth successful"