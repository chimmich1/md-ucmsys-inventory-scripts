from observations.category_pricing import category_pricing

def test_category_pricing_preserves_provider_pricing_and_cabins():
    result=category_pricing({"categories":[{"categoryCode":"E2","pricing":{"amount":1234.5},"cabins":[{"cabinNumber":"10166"}]}]})
    assert result == [{"categoryCode":"E2","pricing":{"amount":1234.5},"cabins":["10166"]}]

def test_category_pricing_handles_missing_categories():
    assert category_pricing({}) == []
