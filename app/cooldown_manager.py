from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

# Cooldown caches
resend_verification_cache = {}
reset_password_cache = {}

def clean_expired_cache(cache: dict, cooldown_period: timedelta):
    """
    Removes expired cooldown entries from the provided cache.
    """
    now = datetime.now(timezone.utc)
    expired_keys = [email for email, timestamp in cache.items() if now - timestamp > cooldown_period]
    for email in expired_keys:
        del cache[email]

def check_and_update_cooldown(cache: dict, email: str, cooldown_period: timedelta, error_message: str):
    """
    Cleans expired entries, checks if the given email is under cooldown, and updates the cooldown cache.

    Raises:
        HTTPException (429) if cooldown is still active.
    """
    now = datetime.now(timezone.utc)

    # Clean old entries
    clean_expired_cache(cache, cooldown_period)

    last_request_time = cache.get(email)
    if last_request_time and now - last_request_time < cooldown_period:
        raise HTTPException(status_code=429, detail=error_message)

    # Set new cooldown time
    cache[email] = now
