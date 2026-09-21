from pathlib import Path
import json
from observations.celebrity_json_inventory import publish

def test_publish_is_readable_json(tmp_path):
    target=tmp_path/'observations.json'
    publish(target, [{"requestedDeckCode":"02"}])
    assert json.loads(target.read_text()) == [{"requestedDeckCode":"02"}]
    assert not target.with_suffix('.json.tmp').exists()
