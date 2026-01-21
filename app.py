from flask import Flask, jsonify
import requests
import secrets
import string
import os

app = Flask(__name__)

def generate_nonce(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "femboymodding api",
        "endpoint": "/meta/access_token=<ACCESS_TOKEN>",
        "adds": ["nonce"],
        "fields": [
            "user_id",
            "org_scoped_id"
        ]
    })

@app.route("/meta/access_token=<access_token>", methods=["GET"])
def meta_passthrough(access_token):
    try:
        r = requests.get(
            "https://graph.oculus.com/me",
            params={
                "access_token": access_token,
                "fields": "id,org_scoped_id"  # only fetch what we need
            },
            timeout=10
        )
        data = r.json()

        # rename id → user_id
        user_id = data.get("id")
        org_scoped_id = data.get("org_scoped_id")
        response = {
            "user_id": user_id,
            "org_scoped_id": org_scoped_id,
            "nonce": generate_nonce()
        }

        return jsonify(response), r.status_code

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "request to Meta failed",
            "details": str(e),
            "nonce": generate_nonce()
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
