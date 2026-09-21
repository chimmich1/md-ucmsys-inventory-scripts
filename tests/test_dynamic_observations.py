from observations.celebrity_v15_to_universal import convert_record


def test_archived_celebrity_record_maps_to_universal_contract():
    record = {
        "voyageId": "XC07E474_2027-03-07", "observedAtUtc": "2026-09-20T12:00:00+00:00",
        "packageCode": "XC07E474", "sailDate": "2027-03-07", "shipCode": "XC",
        "market": {"countryCode": "CAN", "currency": "CAD"}, "occupancy": {"adults": 2, "children": 0},
        "category": {"categoryCode": "E2"}, "cabin": {"number": "10166", "deck": {"code": "10"}, "location": "MIDSHIP", "sourcePath": "roomNumbers.categories[].cabins[]"},
        "availability": {"status": "AVAILABLE", "inventoryCompleteForCategory": False, "partialReason": "unselected decks"},
        "pricing": {"scope": "EXACT_CABIN", "requestedFareCode": "BESTRATE"},
        "source": {"provider": "CELEBRITY", "roomLocationUrl": "https://www.celebritycruises.com/room-selection/room-location", "checkoutEndpoint": "https://www.celebritycruises.com/checkout/api/v1/rooms/checkout"},
        "checkoutResponse": {"rooms": [{"roomNumber": "10166"}]},
    }
    result = convert_record(record)
    assert result["schemaVersion"] == "1.1"
    assert result["cabin"]["cabinNumber"] == "10166"
    assert result["availability"]["inventoryCompleteForCategory"] is False
    assert result["checkout"]["rooms"][0]["roomNumber"] == "10166"
