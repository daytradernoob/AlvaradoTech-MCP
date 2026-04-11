"""
PredictaNoob — Kalshi Auth
RSA-PSS signature auth for api.elections.kalshi.com
Signature rule: timestamp_ms + METHOD + /trade-api/v2/path
"""
import os, time, base64
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

ENV_PATH = "/home/rob-alvarado/RJA/.pnb/.env"
BASE_URL  = "https://api.elections.kalshi.com/trade-api/v2"
SIGN_PREFIX = "/trade-api/v2"

_key_cache = None

def _load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        for line in open(ENV_PATH):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def _private_key():
    global _key_cache
    if _key_cache:
        return _key_cache
    env = _load_env()
    pem_path = env.get("KALSHI_PRIVATE_KEY_PATH", "")
    with open(pem_path, "rb") as f:
        _key_cache = serialization.load_pem_private_key(f.read(), password=None)
    return _key_cache

def headers(method, path):
    """Return signed headers for a Kalshi API request. path = /portfolio/balance etc."""
    env = _load_env()
    key_id = env["KALSHI_API_KEY"]
    ts = str(int(time.time() * 1000))
    msg = (ts + method.upper() + SIGN_PREFIX + path).encode()
    sig = _private_key().sign(
        msg,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return {
        "KALSHI-ACCESS-KEY": key_id,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
        "Content-Type": "application/json"
    }

def get(path, params=None):
    return requests.get(BASE_URL + path, headers=headers("GET", path), params=params, timeout=15)

def post(path, body):
    return requests.post(BASE_URL + path, headers=headers("POST", path), json=body, timeout=15)

def is_live():
    env = _load_env()
    return env.get("LIVE_TRADING", "false").lower() == "true"

def min_balance_cents():
    env = _load_env()
    return int(env.get("MIN_BALANCE_CENTS", "2000"))
