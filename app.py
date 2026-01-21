from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Your organization ID (from Meta)
ORG_ID = "25772455072442378"

GRAPH_URL = "https://graph.oculus.com"

@app.route("/get_user_info", methods=["POST"])
def get_user_info():
    data = request.json
    if not data or "access_token" not in data:
        return jsonify({"error": "Missing access_token"}), 400

    user_token = data["access_token"]

    # Step 1: Get user ID
    user_info_url = f"{GRAPH_URL}/me"
    headers = {"Authorization": f"Bearer {user_token}"}
    resp = requests.get(user_info_url, headers=headers)

    if resp.status_code != 200:
        return jsonify({
            "error": "Failed to validate access token",
            "details": resp.text
        }), resp.status_code

    user_data = resp.json()
    user_id = user_data.get("id")
    if not user_id:
        return jsonify({"error": "Could not fetch user ID"}), 500

    # Step 2: Generate a valid nonce for this user
    nonce_url = f"{GRAPH_URL}/{user_id}/user_nonce_generate"
    resp_nonce = requests.post(nonce_url, headers=headers)

    if resp_nonce.status_code != 200:
        return jsonify({
            "error": "Failed to generate nonce",
            "details": resp_nonce.text
        }), resp_nonce.status_code

    nonce_data = resp_nonce.json()
    nonce = nonce_data.get("nonce")
    if not nonce:
        return jsonify({"error": "Nonce generation failed", "details": nonce_data}), 500

    # Step 3: Construct org-scoped ID
    org_scoped_id = f"{user_id}_{ORG_ID}"

    # Step 4: Return everything
    return jsonify({
        "nonce": nonce,
        "user_id": user_id,
        "org_scope_id": org_scoped_id,
        "org_id": ORG_ID
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
