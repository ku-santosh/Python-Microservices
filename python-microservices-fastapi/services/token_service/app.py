from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt, os
from dotenv import load_dotenv

stage = os.environ.get('STAGE','dev'); load_dotenv(dotenv_path=f'.env.{stage}', override=True)
JWT_SECRET = os.environ.get('JWT_SECRET','devsecret')

app = FastAPI(title='Token Service')

class TokenIn(BaseModel):
    token: str

@app.post('/introspect')
def introspect(payload: TokenIn):
    try:
        payload_jwt = jwt.decode(payload.token, JWT_SECRET, algorithms=['HS256'])
        return {'active': True, 'user_id': payload_jwt.get('user_id')}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token_expired')
    except Exception:
        raise HTTPException(status_code=401, detail='invalid_token')
