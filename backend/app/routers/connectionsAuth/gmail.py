from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
import os
from dotenv import load_dotenv
from app.dependencies.auth import get_current_user
from app.models.user import User




load_dotenv()

router = APIRouter(prefix="/auth/gmail", tags=["Gmail OAuth"])


SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "openid",     
    "email",
    "profile"
]


CLIENT_CONFIG = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [os.getenv("REDIRECT_URI")],
    }
}


def create_flow() -> Flow:
    return Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=os.getenv("REDIRECT_URI")
    )


@router.get("/connect")
def connect_gmail(current_user:User=Depends(get_current_user)):
   
    flow = create_flow()
    
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=str(current_user.id), 
        include_granted_scopes="true"
    )
    
    return {"url": auth_url}


@router.get("/callback")
def gmail_callback(
    code: str,          
    state: str,        
    #db: Session = Depends(get_db)
):
   
    flow = create_flow()
    
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")
    
    creds = flow.credentials
    user_id = int(state)
    
    gmail_email = None
    if creds.id_token:
        from jose import jwt as jose_jwt
        claims = jose_jwt.get_unverified_claims(creds.id_token)
        gmail_email = claims.get("email")
    
    #existing_token = db.query(GoogleToken).filter_by(user_id=user_id).first()
    
    if existing_token:
        existing_token.access_token = encrypt_token(creds.token)
        existing_token.refresh_token = encrypt_token(creds.refresh_token)
        existing_token.token_expiry = creds.expiry
        existing_token.gmail_email = gmail_email
    else:
        new_token = GoogleToken(
            user_id=user_id,
            access_token=encrypt_token(creds.token),      
            refresh_token=encrypt_token(creds.refresh_token),
            token_expiry=creds.expiry,
            gmail_email=gmail_email
        )
        #db.add(new_token)
    
   # db.commit()
    
    # Redirect the user's browser back to React frontend
    frontend_url = os.getenv("FRONTEND_URL")
    return RedirectResponse(f"{frontend_url}/dashboard?gmail=connected")


@router.delete("/disconnect")
def disconnect_gmail(
    current_user=Depends(get_current_user),
   # db: Session = Depends(get_db)
):
   
    #token_row = db.query(GoogleToken).filter_by(user_id=current_user.id).first()
    if not token_row:
        raise HTTPException(status_code=404, detail="Gmail not connected")
    
    #db.delete(token_row)
    #db.commit()
    return {"message": "Gmail disconnected successfully"}


def get_gmail_service(user_id: int, db: Session):
    from googleapiclient.discovery import build
    
    #token_row = db.query(GoogleToken).filter_by(user_id=user_id).first()
    if not token_row:
        raise HTTPException(status_code=403, detail="Gmail not connected. Please connect Gmail first.")
    
    # Decrypt tokens from DB
    #access_token = decrypt_token(token_row.access_token)
    #refresh_token = decrypt_token(token_row.refresh_token)
    
    # Rebuild Credentials object from stored values
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=SCOPES
    )
    
    # Auto-refresh if access_token is expired
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        
        # Save the new access_token back to DB (refresh_token stays the same)
        token_row.access_token = encrypt_token(creds.token)
        token_row.token_expiry = creds.expiry
        db.commit()
    
    # build() creates the Gmail API client — authenticated with this user's creds
    return build("gmail", "v1", credentials=creds)

