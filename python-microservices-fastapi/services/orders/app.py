from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import jwt, os
from dotenv import load_dotenv
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

stage = os.environ.get('STAGE','dev'); load_dotenv(dotenv_path=f'.env.{stage}', override=True)
JWT_SECRET = os.environ.get('JWT_SECRET','devsecret')

app = FastAPI(title='Orders Service')

class OrderIn(BaseModel):
    product_id: int
    quantity: int = 1

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail='token_missing')
    token = authorization.split(' ',1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='token_expired')
    except Exception:
        raise HTTPException(status_code=401, detail='token_invalid')

@app.post('/orders')
def create_order(order: OrderIn, user_id: int = Depends(get_current_user)):
    stub = get_stub()
    req = pb2.CreateOrderRequest(user_id=user_id, product_id=order.product_id, quantity=order.quantity)
    res = stub.CreateOrder(req)
    if res.error:
        raise HTTPException(status_code=500, detail=res.error)
    return {'id': res.id, 'user_id': user_id, 'product_id': order.product_id, 'quantity': order.quantity, 'status':'created'}

@app.get('/orders')
def list_orders(user_id: int = Depends(get_current_user)):
    stub = get_stub()
    req = pb2.ListOrdersRequest(user_id=user_id)
    res = stub.ListOrders(req)
    return [{'id': o.id, 'product_id': o.product_id, 'quantity': o.quantity, 'status': o.status} for o in res.orders]
