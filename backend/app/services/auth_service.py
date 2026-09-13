import hashlib
import hmac
import time
import json
import base64
from typing import Dict, Any, Optional

SECRET_KEY = "worksight-ai-enterprise-secret-key-production-grade"

class AuthService:
    """Enterprise authentication, PBKDF2 password hashing, and Role-Based Access Control (RBAC)."""

    ROLES = ["Admin", "HR Director", "HR Manager", "Manager", "Employee"]

    ROLE_PERMISSIONS = {
        "Admin": ["view_all", "edit_all", "manage_users", "approve_actions", "view_audit", "run_simulations", "manage_models"],
        "HR Director": ["view_all", "edit_all", "approve_actions", "view_audit", "run_simulations"],
        "HR Manager": ["view_all", "edit_candidates", "create_actions", "run_simulations", "view_audit"],
        "Manager": ["view_team", "view_performance", "recommend_action"],
        "Employee": ["view_self", "view_onboarding", "query_policy"]
    }

    def hash_password(self, password: str) -> str:
        salt = b"worksight_salt_2026"
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return key.hex()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return hmac.compare_digest(self.hash_password(plain_password), hashed_password)

    def generate_token(self, username: str, role: str, full_name: str) -> str:
        payload = {
            "sub": username,
            "role": role,
            "name": full_name,
            "exp": int(time.time()) + 86400 * 7 # 7 days
        }
        encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
        signature = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
        return f"{encoded_payload}.{signature}"

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split('.')
            if len(parts) != 2:
                return None
            encoded_payload, signature = parts
            expected_signature = hmac.new(SECRET_KEY.encode(), encoded_payload.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_signature):
                return None
            padding = '=' * (4 - len(encoded_payload) % 4)
            payload = json.loads(base64.urlsafe_b64decode(encoded_payload + padding).decode())
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None

    def mask_pii(self, text: str) -> str:
        """Masks sensitive email addresses and phone numbers to protect candidate privacy."""
        import re
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED_PHONE]', text)
        return text

auth_service = AuthService()
