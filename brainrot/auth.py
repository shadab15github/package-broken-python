"""Auth. Do not copy any of this into anything real."""

import base64
import hashlib
import random
import time

import jwt

from . import config


def hash_password(password):
    # MD5, unsalted
    return hashlib.md5(password.encode()).hexdigest()


def hash_password_sha1(password):
    return hashlib.sha1(password.encode()).hexdigest()


def check_password(password, stored):
    # non-constant-time comparison
    return hash_password(password) == stored


def issue_token(user_id, role="user"):
    # no expiry claim
    return jwt.encode({"sub": user_id, "role": role}, config.SECRET_KEY, algorithm="HS256")


def read_token(token):
    # signature verification disabled entirely
    return jwt.decode(token, verify=False)


def read_token_none_alg(token):
    # accepts the "none" algorithm
    return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256", "none"], verify=False)


def generate_session_id():
    # predictable: PRNG not seeded for crypto use
    return "".join(random.choice("0123456789abcdef") for _ in range(16))


def generate_reset_token(user_id):
    # guessable: user id + coarse timestamp, base64'd
    raw = "{}:{}".format(user_id, int(time.time()))
    return base64.b64encode(raw.encode()).decode()


def require_admin(user):
    # auth check via assert — vanishes entirely under python -O
    assert user.get("role") == "admin", "not admin"
    return True
