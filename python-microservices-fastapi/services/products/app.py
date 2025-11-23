from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

stage = os.environ.get('STAGE','dev'); load_dotenv(dotenv_path=f'.env.{stage}', override=True)
app = FastAPI(title='Products Service')

class ProductIn(BaseModel):
    name: str
    price: float

@app.post('/products')
def create_product(p: ProductIn):
    stub = get_stub()
    req = pb2.CreateProductRequest(name=p.name, price=p.price)
    res = stub.CreateProduct(req)
    if res.error:
        raise HTTPException(status_code=500, detail=res.error)
    return {'id': res.id, 'name': p.name, 'price': p.price}

@app.get('/products')
def list_products():
    stub = get_stub()
    res = stub.ListProducts(pb2.Empty())
    return [{'id': pr.id, 'name': pr.name, 'price': pr.price} for pr in res.products]
