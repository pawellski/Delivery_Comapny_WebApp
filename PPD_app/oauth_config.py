import os

OAUTH_BASE_URL = "https://spawel-pamiw.eu.auth0.com"
OAUTH_ACCESS_TOKEN_URL = OAUTH_BASE_URL + "/oauth/token"
OAUTH_AUTHORIZE_URL = OAUTH_BASE_URL + "/authorize"
OAUTH_CALLBACK_LOGIN_URL = "https://localhost:8080/callback"
OAUTH_CALLBACK_COURIER_URL = "https://localhost:8083/callback"
OAUTH_CLIENT_ID = "7UOe0zdM5EsJoQ9p7QrKUDw8pnljyBa4"
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
OAUTH_SCOPE = "openid profile"
SECRET_KEY = os.environ.get("LAB_AUTH_SECRET")
NICKNAME = "nickname"