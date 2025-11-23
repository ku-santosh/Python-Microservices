import os
import requests
from flask import Flask, request, jsonify

DB_PROXY_HOST = os.getenv("DB_PROXY_HOST", "db-proxy")
DB_PROXY_PORT = os.getenv("DB_PROXY_PORT", "5000")
DB_PROXY_BASE = f"http://{DB_PROXY_HOST}:{DB_PROXY_PORT}"

app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"}), 200

@app.route("/api/v1/perspectives", methods=["GET"])
def get_all_perspectives():
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["GET"])
def get_by_id(pid):
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/{pid}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/user/<string:username>", methods=["GET"])
def get_by_user(username):
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives", methods=["POST"])
def create_perspective():
    payload = request.get_json()
    try:
        r = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["PUT"])
def update_perspective(pid):
    payload = request.get_json()
    try:
        r = requests.put(f"{DB_PROXY_BASE}/perspectives/{pid}", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/username/<string:username>", methods=["PUT"])
def update_perspective_by_username(username):
    payload = request.get_json()
    try:
        r = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=payload, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/perspectives/<int:pid>", methods=["DELETE"])
def delete_perspective(pid):
    try:
        r = requests.delete(f"{DB_PROXY_BASE}/perspectives/{pid}", timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.getenv("PORT", 5001))
    app.run(host=host, port=port)
