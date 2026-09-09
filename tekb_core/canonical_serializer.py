# C:\Users\lenovo\phase1\tekb_core\canonical_serializer.py
import json, hashlib

def canonical_serialize(payload: dict) -> bytes:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return canonical_json.encode('utf-8')

def compute_configuration_hash(payload: dict) -> str:
    return hashlib.sha256(canonical_serialize(payload)).hexdigest()