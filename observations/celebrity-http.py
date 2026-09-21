import json, sys

try:
    from curl_cffi import requests
except ImportError:
    print(json.dumps({
        "transport_error": "curl_cffi is not installed. Run: python -m pip install curl_cffi"
    }))
    sys.exit(2)

APPKEY_WEB = "hyNNqIPHHzaLzVpcICPdAdbFV8yvTsAm"

def main():
    req = json.load(sys.stdin)
    method = req.get("method", "GET").upper()
    url = req["url"]
    headers = dict(req.get("headers") or {})
    body = req.get("body")
    timeout = req.get("timeout", 45)

    headers.setdefault("AppKey", APPKEY_WEB)

    session = requests.Session(impersonate="chrome")

    if method == "GET":
        r = session.get(url, headers=headers, timeout=timeout)
    elif method == "POST":
        if isinstance(body, (dict, list)):
            r = session.post(url, headers=headers, json=body, timeout=timeout)
        else:
            r = session.post(url, headers=headers, data=body, timeout=timeout)
    else:
        raise ValueError(f"Unsupported method: {method}")

    out = {
        "status": r.status_code,
        "url": r.url,
        "headers": dict(r.headers),
        "text": r.text
    }
    json.dump(out, sys.stdout)

if __name__ == "__main__":
    main()
