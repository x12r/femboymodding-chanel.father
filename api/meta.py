import json
import requests
import secrets
import string

def generate_nonce(length=64):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def handler(request):
    path = request.path

    # Homepage: shows API info
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
            }, indent=2)
        }

    # Passthrough endpoint
    if "access_token=" in path:
        token = path.split("access_token=", 1)[1]

        try:
            r = requests.get(
                "https://graph.oculus.com/me",
                params={
                    "access_token": token,
                    "fields": "display_name,alias,org_scoped_id,email"
                },
                timeout=10
            )

            data = r.json()
            data["nonce"] = generate_nonce()

            return {
                "statusCode": r.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(data, indent=2)
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
                }, indent=2)
            }

    # Catch all for unknown paths
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "not found"}, indent=2)
    }
