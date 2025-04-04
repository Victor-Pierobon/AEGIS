import os
import logging
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import Config

def authenticate_google():
    """Autentica o usuário com Google OAuth2"""
    try:
        logging.info("Starting Google authentication")
        creds = None
        
        # Verifica se já existe um token
        if Config.Google.TOKEN_PATH.exists():
            logging.info("Found existing token, loading credentials")
            creds = Credentials.from_authorized_user_file(
                Config.Google.TOKEN_PATH, 
                Config.Google.SCOPES
            )
        
        # Se não há credenciais ou elas estão expiradas
        if not creds or not creds.valid:
            logging.info("Credentials invalid or missing, starting authorization flow")
            
            if creds and creds.expired and creds.refresh_token:
                logging.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logging.info("Creating new credentials with user login")
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.Google.CREDS_PATH, 
                    Config.Google.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Salva credenciais
            with open(Config.Google.TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
                logging.info("Credentials saved to file")
                
        logging.info("Google authentication completed successfully")
        return creds
        
    except Exception as e:
        logging.error(f"Error during Google authentication: {str(e)}", exc_info=True)
        return None