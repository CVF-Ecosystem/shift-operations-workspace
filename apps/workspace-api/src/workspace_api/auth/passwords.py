"""Password hashing (P2-B: real authentication).

bcrypt, not passlib/argon2-cffi - actively maintained with prebuilt wheels on
every platform this repo targets (including Windows dev machines), and the
hashpw/checkpw API is all this module needs.
"""

from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))


# Independent review (2026-07-22) found a timing side-channel in the login
# endpoint: when a username doesn't exist, `verify_password` was never
# called at all, making an unknown-username response ~18x faster than a
# wrong-password response - a measurable username-enumeration vector even
# though the response body/status were identical. Comparing against this
# precomputed dummy hash when no user is found costs the same bcrypt work as
# a real check, closing the timing gap.
DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-equalization")
