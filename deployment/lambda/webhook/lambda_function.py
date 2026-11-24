import hashlib
import hmac
import json
import os
import urllib.request
from urllib.parse import urlsplit

import boto3


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def lambda_handler(event, _context):
    raw = boto3.client("secretsmanager").get_secret_value(
        SecretId=os.environ["WEBHOOK_SECRET_ARN"]
    )["SecretString"]
    creds = json.loads(raw)
    url = creds.get("webhookUrl", "")
    secret = creds.get("webhookSecret", "")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname
            or parsed.username or parsed.password
            or parsed.hostname != os.environ["APPROVED_WEBHOOK_HOST"]
            or not secret or secret.startswith("REPLACE")):
        return {"ok": False, "error": "webhook secret is still a placeholder"}
    body = json.dumps(event).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=" + signature,
        },
        method="POST",
    )
    with urllib.request.build_opener(_NoRedirect()).open(request, timeout=10) as response:
        return {"ok": True, "status": response.status}
