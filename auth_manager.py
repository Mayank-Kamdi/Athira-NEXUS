import time
import json
import os
import requests
from datetime import datetime, timedelta

class RateLimiter:
    """Simple rate limiter to prevent brute force attacks."""
    def __init__(self, limit=5, window_seconds=300):
        self.attempts = {}
        self.limit = limit
        self.window = window_seconds

    def is_blocked(self, identity):
        now = time.time()
        if identity not in self.attempts:
            return False
        
        # Filter attempts within the window
        valid_attempts = [t for t in self.attempts[identity] if now - t < self.window]
        self.attempts[identity] = valid_attempts
        
        return len(valid_attempts) >= self.limit

    def record_attempt(self, identity):
        now = time.time()
        if identity not in self.attempts:
            self.attempts[identity] = []
        self.attempts[identity].append(now)

    def clear(self, identity):
        if identity in self.attempts:
            del self.attempts[identity]

class AuthManager:
    """Handles Auth logic (Placeholder for Firebase/Custom integration)."""
    def __init__(self):
        self.rate_limiter = RateLimiter()
        # In a real app, these would come from environment variables
        self.api_key = os.environ.get("FIREBASE_API_KEY", "MOCK_API_KEY")
        
    def sign_up(self, email, password):
        """Simulates Firebase Signup with Email Verification."""
        # Real implementation: requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}", ...)
        return {"status": "success", "message": "VERIFICATION_EMAIL_SENT", "email": email}

    def login(self, email, password):
        """Simulates Firebase Login with Rate Limiting."""
        if self.rate_limiter.is_blocked(email):
            return {"status": "error", "message": "BRUTE_FORCE_PROTECTION_ACTIVE. TRY_AGAIN_IN_5_MINS"}
        
        # Mocking check for demo
        if email == "admin@aithra.io" and password == "secure123":
            self.rate_limiter.clear(email)
            return {"status": "success", "token": "MOCK_JWT_TOKEN"}
        
        self.rate_limiter.record_attempt(email)
        return {"status": "error", "message": "INVALID_CREDENTIALS"}

    def reset_password(self, email):
        """Simulates Password Reset Flow."""
        return {"status": "success", "message": "PASSWORD_RESET_LINK_SENT"}

    def oauth_google(self):
        """Placeholder for Google OAuth URL generation."""
        return "https://accounts.google.com/o/oauth2/auth?..."

def track_event(user_id, event_type, metadata=None):
    """Simple user event tracking for analytics."""
    log_file = "analytics_events.json"
    event = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "event": event_type,
        "metadata": metadata or {}
    }
    try:
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(event)
        with open(log_file, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass
