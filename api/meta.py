from flask import Flask, jsonify
import requests
import secrets
import string

app = Flask(__name__)

def generate_nonce(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "femboymodding api",
        "endpoints": {
            "meta_passthrough": "/api/meta/access_token=<ACCESS_TOKEN>"
        },
        "forwards_to": "https://graph.oculus.com/me",
        "fields": [
            "display_name",
            "alias",
            "org_scoped_id",
            "email"
        ],
        "adds": ["nonce"]
    })

@app.route("/access_token=<access_token>", methods=["GET"])
def meta_passthrough(access_token):
    try:
        r = requests.get(
            "https://graph.oculus.com/me",
            params={
                "access_token": access_token,
                "fields": "display_name,alias,org_scoped_id,email"
            },
            timeout=10
        )

        meta_json = r.json()

        # Always add nonce to response
        meta_json["nonce"] = generate_nonce()

        return jsonify(meta_json), r.status_code

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "request to Meta failed",
            "details": str(e),
            "nonce": generate_nonce()
        }), 500

# Vercel entrypoint
def handler(request, *args, **kwargs):
    return app(request.environ, start_response=lambda *x: None)
