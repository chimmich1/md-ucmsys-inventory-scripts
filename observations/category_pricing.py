"""Normalize category-level pricing from Celebrity roomNumbers JSON."""
from __future__ import annotations
from typing import Any

def category_pricing(room_numbers: dict[str, Any]) -> list[dict[str, Any]]:
    result=[]
    for category in room_numbers.get("categories", []) or []:
        if not isinstance(category, dict): continue
        pricing = category.get("pricing")
        result.append({
            "categoryCode": category.get("categoryCode", category.get("code")),
            "pricing": pricing,
            "cabins": [c.get("cabinNumber") for c in category.get("cabins", []) if isinstance(c, dict) and c.get("cabinNumber") is not None],
        })
    return result
