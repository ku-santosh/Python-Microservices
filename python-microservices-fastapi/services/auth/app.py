from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

stage = os.environ.get('STAGE','dev'); load_dotenv(dotenv_path=f'.env.{stage}', override=True)
JWT_SECRET = os.environ.get('JWT_SECRET','devsecret')

app = FastAPI(title='Auth Service')

class RegisterIn(BaseModel):
    username: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

@app.post('/register')
def register(payload: RegisterIn):
    stub = get_stub()
    pw_hash = payload.password  # in real app, hash before sending
    req = pb2.CreateUserRequest(username=payload.username, password_hash=pw_hash)
    res = stub.CreateUser(req)
    if res.error:
        raise HTTPException(status_code=500, detail=res.error)
    return {'message':'User registered','id': res.id}

@app.post('/login')
def login(payload: LoginIn):
    stub = get_stub()
    req = pb2.GetUserRequest(username=payload.username)
    res = stub.GetUserByUsername(req)
    if res.error:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    # check password (omitted)
    token = jwt.encode({'user_id': res.id, 'exp': datetime.utcnow()+timedelta(hours=2)}, JWT_SECRET, algorithm='HS256')
    return {'access_token': token}
