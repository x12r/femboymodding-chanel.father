import json
import requests
import secrets
import string

def generate_nonce(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def handler(request):
    path = request.path

    # Homepage
    if path == "/api/meta":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "service": "femboymodding api",
                "endpoint": "/api/meta/access_token=<ACCESS_TOKEN>",
                "forwards_to": "https://graph.oculus.com/me",
                "fields": [
                    "display_name",
                    "alias",
                    "org_scoped_id",
                    "email"
                ],
                "adds": ["nonce"]
            })
        }

    # Access token passthrough
    if "access_token=" in path:
        access_token = path.split("access_token=", 1)[1]

        try:
            r = requests.get(
                "https://graph.oculus.com/me",
                params={
                    "access_token": access_token,
                    "fields": "display_name,alias,org_scoped_id,email"
                },
                timeout=10
            )

            data = r.json()
            data["nonce"] = generate_nonce()

            return {
                "statusCode": r.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(data)
            }

        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "error",
                    "message": "request to Meta failed",
                    "details": str(e),
                    "nonce": generate_nonce()
                })
            }

    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "not found"})
    }
