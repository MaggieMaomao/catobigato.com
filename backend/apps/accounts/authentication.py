"""
Custom Keycloak JWT authentication for Django REST Framework.
Validates access tokens issued by Keycloak at https://www.keytomarvel.com/realms/catobigato
"""

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.request import Request


class KeycloakUser:
    """Lightweight user object derived from Keycloak JWT claims."""

    def __init__(self, payload: dict):
        self.sub = payload.get("sub", "")
        self.email = payload.get("email", "")
        self.username = payload.get("preferred_username", "")
        self.first_name = payload.get("given_name", "")
        self.last_name = payload.get("family_name", "")
        self.is_authenticated = True
        self.is_active = payload.get("email_verified", True)
        self.is_staff = "admin" in payload.get("roles", [])
        self.payload = payload

    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __str__(self) -> str:
        return self.username or self.sub


class KeycloakAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class that validates JWTs from Keycloak.

    Usage:
      class MyView(APIView):
          authentication_classes = [KeycloakAuthentication]
    """

    keyword = "Bearer"

    def authenticate(self, request: Request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header[len(self.keyword) + 1:]

        try:
            payload = self._verify_token(token)
            user = KeycloakUser(payload)
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f"Invalid token: {e}")

    def _verify_token(self, token: str) -> dict:
        """Fetch Keycloak JWKS and validate the JWT signature + claims."""
        # Get the key ID (kid) from token header
        try:
            unverified_header = jwt.get_unverified_header(token)
        except jwt.DecodeError:
            raise jwt.InvalidTokenError("Malformed token header")

        kid = unverified_header.get("kid")
        if not kid:
            raise jwt.InvalidTokenError("Token missing key ID (kid) in header")

        # Fetch JWKS from Keycloak
        jwks_url = f"{settings.KEYCLOAK_URL}/protocol/openid-connect/certs"
        try:
            jwks_client = jwt.PyJWKClient(jwks_url, cache_keys=True)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
        except Exception as e:
            raise jwt.InvalidTokenError(f"Failed to fetch signing key: {e}")

        # Decode and verify — RS256 is default for Keycloak
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
            audience=settings.KEYCLOAK_CLIENT_ID,
            issuer=settings.KEYCLOAK_URL + "/realms/" + settings.KEYCLOAK_REALM,
        )
        return payload

    def authenticate_header(self, request: Request) -> str:
        return f'{self.keyword} realm="catobigato"'