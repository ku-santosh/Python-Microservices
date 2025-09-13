from flask import Flask, request, jsonify
import jwt, os
from dotenv import load_dotenv
stage = os.environ.get('STAGE','dev')
load_dotenv(dotenv_path=f'.env.{stage}', override=True)
SECRET = os.environ.get('JWT_SECRET','devsecret')
app = Flask(__name__)

@app.route('/introspect', methods=['POST'])
def introspect():
    if not request.is_json:
        return jsonify({'error':'JSON required'}), 415
    token = request.get_json().get('token')
    if not token:
        return jsonify({'error':'token required'}), 400
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return jsonify({'active': True, 'user_id': payload.get('user_id')}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'active': False, 'error': 'token_expired'}), 401
    except Exception:
        return jsonify({'active': False, 'error': 'invalid_token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5004)))
