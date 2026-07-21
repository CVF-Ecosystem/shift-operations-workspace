import hashlib, hmac
from integration_edge.verification.hmac import verify_hmac

def test_hmac_verification():
    body=b"{}"; secret="s"; sig=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
    assert verify_hmac(body,sig,secret)
    assert not verify_hmac(body,"bad",secret)
