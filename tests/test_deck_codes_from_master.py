from observations.deck_codes_from_master import deck_codes

def test_deck_codes_from_master():
    assert deck_codes({"groups": [{"classDefaults": [{"field": "deckNumber", "value": 10}, {"field": "deckNumber", "value": 2}], "shipOverrides": []}]}) == ["02", "10"]
