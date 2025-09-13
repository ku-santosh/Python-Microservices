from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import jwt
from services.common.db_client import get_stub
import proto.db_service_pb2 as pb2

from utils import hash_password, check_password

stage = os.environ.get('STAGE', 'dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)
SECRET_KEY = os.environ.get('JWT_SECRET', 'devsecret')

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 415
    data = request.get_json()
    username = data.get('username'); password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    stub = get_stub()
    pw_hash = hash_password(password)
    req = pb2.CreateUserRequest(username=username, password_hash=pw_hash)
    res = stub.CreateUser(req)
    if res.error:
        return jsonify({'error': res.error}), 500
    return jsonify({'message': 'User registered successfully', 'id': res.id}), 201

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'error': 'JSON required'}), 415
    data = request.get_json()
    username = data.get('username'); password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    stub = get_stub()
    req = pb2.GetUserRequest(username=username)
    res = stub.GetUserByUsername(req)
    if res.error:
        return jsonify({'error': 'Invalid username or password'}), 401
    if not check_password(password, res.password_hash):
        return jsonify({'error': 'Invalid username or password'}), 401
    token = jwt.encode({'user_id': res.id, 'exp': datetime.utcnow()+timedelta(hours=2)}, SECRET_KEY, algorithm='HS256')
    return jsonify({'access_token': token}), 200

if __name__ == '__main__':
    # health check to print DB connection status
    from services.common.db_client import wait_for_db_service
    wait_for_db_service(timeout=10)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5001)))
