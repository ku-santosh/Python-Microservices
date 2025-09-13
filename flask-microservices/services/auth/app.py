from flask import Flask, request, jsonify, make_response
import jwt, json, os
from datetime import datetime, timedelta
from config import Config
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.exc import IntegrityError
import bcrypt

app = Flask(__name__)
app.config.from_object(Config)

# Setup DB
engine = create_engine(app.config.DATABASE_URL, echo=False, future=True)
metadata = MetaData()

users_table = Table('users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(150), unique=True, nullable=False),
    Column('password_hash', String(200), nullable=False)
)

metadata.create_all(engine)

# Helper functions
def hash_password(plain_text_password: str) -> bytes:
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())

def check_password(plain_text_password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed)

@app.route('/auth/register', methods=['POST'])
def register():
    if not request.is_json:
        return jsonify({'error': 'Unsupported Media Type'}), 415
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400
    hashed = hash_password(password)
    ins = users_table.insert().values(username=username, password_hash=hashed.decode('utf-8'))
    try:
        with engine.begin() as conn:
            result = conn.execute(ins)
            user_id = result.inserted_primary_key[0]
    except IntegrityError:
        return jsonify({'error': 'username already exists'}), 409
    return jsonify({'id': user_id, 'username': username}), 201

@app.route('/auth', methods=['POST'])
def authenticate_user():
    if not request.is_json:
        return jsonify({'error': 'Unsupported Media Type'}), 415
    username = request.json.get('username')
    password = request.json.get('password')
    with engine.begin() as conn:
        sel = users_table.select().where(users_table.c.username==username)
        row = conn.execute(sel).fetchone()
        if row and check_password(password, row['password_hash'].encode('utf-8')):
            payload = {
                'user_id': row['id'],
                'exp': datetime.utcnow() + timedelta(hours=2)
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            resp = make_response(jsonify({'message': 'Authentication successful'}))
            resp.set_cookie('token', token, httponly=True, samesite='Lax')
            return resp
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/introspect', methods=['POST'])
def introspect():
    token = request.json.get('token')
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({'active': True, 'user_id': data.get('user_id')}), 200
    except Exception:
        return jsonify({'active': False}), 401

if __name__ == '__main__':
    # create an admin user if none exists (dev convenience)
    with engine.begin() as conn:
        sel = users_table.select().limit(1)
        row = conn.execute(sel).fetchone()
        if not row:
            pw = os.environ.get('ADMIN_PASSWORD', 'admin')
            hashed = hash_password(pw)
            conn.execute(users_table.insert().values(username='admin', password_hash=hashed.decode('utf-8')))
    app.run(host='0.0.0.0', port=Config.PORT)
