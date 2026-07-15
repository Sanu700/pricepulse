"""Probe Blinkit with Chrome TLS impersonation (curl_cffi)."""

from textwrap import shorten

try:
    from curl_cffi import requests as creq
except ImportError as e:
    print("curl_cffi missing", e)
    raise SystemExit(1)


def main():
    url = "https://blinkit.com/v1/layout/search"
    headers = {
        "lat": "28.6139",
        "lon": "77.2090",
        "app_client": "consumer_web",
        "access_token": "null",
        "Accept": "application/json",
    }
    r = creq.get(
        url,
        params={"q": "amul butter", "search_type": "type_to_search"},
        headers=headers,
        impersonate="chrome120",
        timeout=20,
    )
    print("status", r.status_code)
    print("url", r.url)
    print("ct", r.headers.get("content-type"))
    print("body", shorten(r.text.replace("\n", " "), 300))
    if r.status_code == 200:
        try:
            data = r.json()
            print("json_keys", list(data)[:20] if isinstance(data, dict) else type(data))
        except Exception as e:
            print("json_err", e)

    # Zepto BFF with impersonation
    zr = creq.post(
        "https://bff-gateway.zepto.com/user-search-service/api/v3/search",
        json={
            "query": "milk",
            "pageNumber": 0,
            "mode": "SHOW_ALL_RESULTS",
            "sessionId": "",
        },
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        impersonate="chrome120",
        timeout=20,
    )
    print("\nzepto status", zr.status_code)
    print("zepto body", shorten(zr.text.replace("\n", " "), 300))


if __name__ == "__main__":
    main()
