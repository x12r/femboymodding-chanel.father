from flask import Flask, jsonify
import requests, secrets, string

app = Flask(__name__)

def generate_nonce(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "femboymodding api",
        "endpoint": "/meta/access_token=<ACCESS_TOKEN>",
        "adds": ["nonce"]
    })

@app.route("/meta/access_token=<access_token>", methods=["GET"])
def meta_passthrough(access_token):
    try:
        r = requests.get(
            "https://graph.oculus.com/me",
            params={"access_token": access_token,
                    "fields": "display_name,alias,org_scoped_id,email"},
            timeout=10
        )
        data = r.json()
        data["nonce"] = generate_nonce()
        return jsonify(data), r.status_code
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "request to Meta failed",
            "details": str(e),
            "nonce": generate_nonce()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
