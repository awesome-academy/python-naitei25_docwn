from constants import (
    MIN_SESSION_REMEMBER,
    MAX_SESSION_REMEMBER
)

def set_session_expiry(request, remember_me=False):
    if not remember_me:
        request.session.set_expiry(MIN_SESSION_REMEMBER)
    else:
        request.session.set_expiry(MAX_SESSION_REMEMBER)
