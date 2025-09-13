from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)

app = Flask(__name__)

@app.route('/products', methods=['POST'])
def create_product():
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 415
    data = request.get_json()
    name = data.get('name'); price = data.get('price')
    if not name or price is None:
        return jsonify({'error': "'name' and 'price' required"}), 400
    stub = get_stub()
    req = pb2.CreateProductRequest(name=name, price=float(price))
    res = stub.CreateProduct(req)
    if res.error:
        return jsonify({'error': res.error}), 500
    return jsonify({'id': res.id, 'name': name, 'price': price}), 201

@app.route('/products', methods=['GET'])
def list_products():
    stub = get_stub()
    res = stub.ListProducts(pb2.Empty())
    prods = [{'id': p.id, 'name': p.name, 'price': p.price} for p in res.products]
    return jsonify(prods), 200

if __name__ == '__main__':
    from services.common.db_client import wait_for_db_service
    wait_for_db_service(timeout=10)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5002)))
