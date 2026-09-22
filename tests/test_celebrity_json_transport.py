from observations.celebrity_json_inventory import request_json

def test_transport_requires_no_browser_symbols():
    assert "browser" not in request_json.__doc__.lower() or "HTTP" in request_json.__doc__
