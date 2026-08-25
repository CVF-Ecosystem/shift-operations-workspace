from integration_edge.verification.hmac import sign_hmac, verify_hmac

META={"endpoint_id":"ep","channel_id":"ch","external_message_id":"m1","timestamp":"2026-08-24T00:00:00Z"}

def test_hmac_binds_exact_metadata_and_body():
    secret=b"s"*32; body=b"{}"; sig=sign_hmac(body,secret,**META)
    assert verify_hmac(body,sig,secret,**META)
    assert not verify_hmac(b"{ }",sig,secret,**META)
    assert not verify_hmac(body,sig,secret,**{**META,"endpoint_id":"other"})

def test_hmac_rejects_placeholder_or_short_secret():
    assert not verify_hmac(b"{}","00","change-me",**META)
