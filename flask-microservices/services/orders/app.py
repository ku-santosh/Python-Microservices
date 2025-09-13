from flask import Flask, request, jsonify
import jwt
from functools import wraps
from config import Config
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, JSON
import json

app = Flask(__name__)
app.config.from_object(Config)

engine = create_engine(app.config.DATABASE_URL, echo=False, future=True)
metadata = MetaData()

orders_table = Table('orders', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, nullable=False),
    Column('items', JSON, nullable=False),
    Column('total', Integer, nullable=False)
)

metadata.create_all(engine)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth = request.headers.get('Authorization')
        if auth and auth.startswith('Bearer '):
            token = auth.split(' ')[1]
        if not token:
            token = request.cookies.get('token')
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        try:
            data = jwt.decode(token, Config.AUTH_SECRET, algorithms=['HS256'])
            request.user_id = data.get('user_id')
        except Exception:
            return jsonify({'error': 'Authorization token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/orders', methods=['POST'])
@token_required
def create_order():
    body = request.get_json() or {}
    order = {
        'user_id': getattr(request, 'user_id', None),
        'items': body.get('items', []),
        'total': body.get('total', 0),
    }
    with engine.begin() as conn:
        res = conn.execute(orders_table.insert().values(user_id=order['user_id'], items=json.dumps(order['items']), total=order['total']))
        order_id = res.inserted_primary_key[0]
        return jsonify({'id': order_id, **order}), 201

@app.route('/orders', methods=['GET'])
@token_required
def list_orders():
    uid = getattr(request, 'user_id', None)
    with engine.begin() as conn:
        sel = orders_table.select().where(orders_table.c.user_id==uid)
        rows = conn.execute(sel).fetchall()
        data = []
        for r in rows:
            data.append({'id': r['id'], 'user_id': r['user_id'], 'items': json.loads(r['items']), 'total': r['total']})
        return jsonify({'data': data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
