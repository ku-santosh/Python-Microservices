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

@app.route("/api/v1/filter_model/save_single_filter", methods=["POST"])
def save_single_filter():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    filters = payload.get("filter_model")
    if filters is None:
        return jsonify({"error":"filter_model required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            existing = r.json()
            existing_filter_model = existing.get("filter_model", [])
            incoming_list = filters if isinstance(filters, list) else [filters]
            by_key = {(f["name"], f["view"]): f for f in existing_filter_model}
            for incoming in incoming_list:
                key = (incoming["name"], incoming["view"])
                if key in by_key:
                    by_key[key]["filters"] = incoming["filters"]
                    by_key[key]["default"] = incoming["default"]
                else:
                    by_key[key] = incoming
            final_list = list(by_key.values())
            update_payload = {"filter_model": final_list}
            if "layout_name" in payload:
                update_payload["layout_name"] = payload["layout_name"]
            if "updated_by" in payload:
                update_payload["updated_by"] = payload["updated_by"]
            resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=update_payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        elif r.status_code == 404:
            if not payload.get("layout_name") or not payload.get("updated_by"):
                return jsonify({"error":"layout_name and updated_by required for new perspective"}), 400
            resp = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        else:
            return jsonify({"error": "db-proxy fetch error", "detail": r.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5003)))
