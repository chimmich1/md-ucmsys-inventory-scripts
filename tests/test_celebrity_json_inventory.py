from observations.celebrity_json_inventory import Job, collect, request_payload

def test_payload_places_deck_in_room_envelope():
    p = request_payload(Job("XC07E474", "2027-03-07"), "BALCONY", "E2", "06")
    assert p["rooms"][0]["room"]["deckCode"] == "06"
    assert p["roomNumbers"] is True

def test_collect_queries_each_master_deck_and_retains_raw():
    calls = []
    def request(payload):
        calls.append(payload)
        code = payload["rooms"][0]["room"]["deckCode"]
        return {"roomNumbers": {"decks": [{"code": code}], "categories": []}}
    out = collect(Job("XC", "2027-01-01"), [("BALCONY", "E2")], ["02", "10"], request)
    assert [x["requestedDeckCode"] for x in out] == ["02", "10"]
    assert len(calls) == 2

def test_collect_fails_closed_when_requested_deck_missing():
    def request(_): return {"roomNumbers": {"decks": [{"code": "02"}]}}
    try: collect(Job("XC", "2027-01-01"), [("BALCONY", "E2")], ["10"], request)
    except RuntimeError as exc: assert "absent" in str(exc)
    else: raise AssertionError("expected fail-closed error")
