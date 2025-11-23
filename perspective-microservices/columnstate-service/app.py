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

@app.route("/api/v1/column_state/save", methods=["POST"])
def save_column_state():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        elif r.status_code == 404:
            resp = requests.post(f"{DB_PROXY_BASE}/perspectives", json=payload, timeout=10)
            return jsonify(resp.json()), resp.status_code
        else:
            return jsonify({"error": "db-proxy fetch error", "detail": r.text}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/column_state/save_single", methods=["POST"])
def save_single():
    payload = request.get_json()
    username = payload.get("username")
    if not username:
        return jsonify({"error":"username required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code == 200:
            existing = r.json()
            incoming = payload.get("column_state")
            if incoming is None:
                return jsonify({"error":"column_state required"}), 400
            incoming_list = incoming if isinstance(incoming, list) else [incoming]
            existing_column_state = existing.get("column_state", [])
            by_name = {c["name"]: c for c in existing_column_state}
            for item in incoming_list:
                name = item["name"]
                item["defaultColumns"] = list(set(item.get("defaultColumns", [])))
                if item.get("default"):
                    for v in by_name.values():
                        v["default"] = False
                if name in by_name:
                    by_name[name].update({
                        "view": item.get("view"),
                        "defaultColumns": item.get("defaultColumns"),
                        "default": item.get("default", False)
                    })
                else:
                    by_name[name] = item
            final_list = list(by_name.values())
            update_payload = {"column_state": final_list}
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

@app.route("/api/v1/column_state/delete_single", methods=["DELETE"])
def delete_single():
    payload = request.get_json()
    username = payload.get("username")
    name_to_delete = payload.get("column_state_name")
    if not username or not name_to_delete:
        return jsonify({"error":"username and column_state_name required"}), 400
    try:
        r = requests.get(f"{DB_PROXY_BASE}/perspectives/user/{username}", timeout=10)
        if r.status_code != 200:
            return jsonify({"error":"perspective not found"}), 404
        existing = r.json()
        original = existing.get("column_state", [])
        updated = [c for c in original if c.get("name") != name_to_delete]
        if len(updated) == len(original):
            return jsonify({"message":"not found"}), 404
        update_payload = {"column_state": updated}
        resp = requests.put(f"{DB_PROXY_BASE}/perspectives/username/{username}", json=update_payload, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)))
