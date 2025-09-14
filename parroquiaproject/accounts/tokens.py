# accounts/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user):
        # ⚡ no depende de last_login
        return f"{user.pk}{user.password}"

custom_token_generator = CustomTokenGenerator()