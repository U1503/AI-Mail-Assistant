import os
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.core.config import get_settings

settings = get_settings()


class GmailService:
    def __init__(self):
        self.creds: Optional[Credentials] = None

    def authenticate(self) -> Credentials:
        """
        Authenticate user using OAuth 2.0
        Handles token loading, refresh, and new login
        """
        token_path = settings.GOOGLE_TOKEN_FILE
        client_secret = settings.GOOGLE_CLIENT_SECRET_FILE
        scopes = settings.gmail_scopes_list()

        # Load existing token
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(
                token_path, scopes
            )

        # If token is invalid or missing, login again
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secret, scopes
                )
                self.creds = flow.run_local_server(port=0)

            # Save token
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())

        return self.creds

    def get_service(self):
        """
        Returns authenticated Gmail API service
        """
        creds = self.authenticate()
        service = build(
            "gmail",
            "v1",
            credentials=creds,
            cache_discovery=False
        )
        return service


# Singleton helper
def get_gmail_service():
    return GmailService().get_service()
