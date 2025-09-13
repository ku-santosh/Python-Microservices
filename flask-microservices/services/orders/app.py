from flask import Flask, request, jsonify
import os, jwt
from functools import wraps
from dotenv import load_dotenv
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)

AUTH_SECRET = os.environ.get('JWT_SECRET', 'devsecret')
app = Flask(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization','')
        token = None
        if auth.startswith('Bearer '):
            token = auth.split(' ',1)[1]
        if not token:
            return jsonify({'error':'token_missing'}), 401
        try:
            payload = jwt.decode(token, AUTH_SECRET, algorithms=['HS256'])
            request.user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'error':'token_expired'}), 401
        except Exception:
            return jsonify({'error':'token_invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/orders', methods=['POST'])
@token_required
def create_order():
    if not request.is_json:
        return jsonify({'error':'JSON required'}), 415
    data = request.get_json()
    product_id = data.get('product_id'); quantity = int(data.get('quantity',1))
    if not product_id:
        return jsonify({'error':'product_id required'}), 400
    stub = get_stub()
    req = pb2.CreateOrderRequest(user_id=request.user_id, product_id=int(product_id), quantity=quantity)
    res = stub.CreateOrder(req)
    if res.error:
        return jsonify({'error': res.error}), 500
    return jsonify({'id': res.id, 'user_id': request.user_id, 'product_id': product_id, 'quantity': quantity, 'status': 'created'}), 201

@app.route('/orders', methods=['GET'])
@token_required
def list_orders():
    stub = get_stub()
    req = pb2.ListOrdersRequest(user_id=request.user_id)
    res = stub.ListOrders(req)
    orders = [{'id': o.id, 'user_id': o.user_id, 'product_id': o.product_id, 'quantity': o.quantity, 'status': o.status} for o in res.orders]
    return jsonify(orders), 200

if __name__ == '__main__':
    from services.common.db_client import wait_for_db_service
    wait_for_db_service(timeout=10)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5003)))
