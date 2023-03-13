import os.path
from pathlib import Path
from typing import NamedTuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.readonly"]

drive_folder = "google_drive"

def get_token(cred_path):
    cred_path = Path(cred_path)
    cred = None
    token_file_path = Path(Path.cwd(), drive_folder, "token.json")

    if token_file_path.exists():
        cred = Credentials.from_authorized_user_file(str(token_file_path), SCOPES)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(cred_path), SCOPES
            )
            cred = flow.run_local_server(port=0)
        with open(token_file_path, 'w') as file:
            file.write(cred.to_json())
        return cred

    return cred

def upload_zip(zip_created_path, credential_path):
    cred = get_token(credential_path)
    zip_name = os.path.basename(zip_created_path)
    try:
        service = build("drive", 'v3', credentials=cred)

        file_metadata = {"name": zip_name, "mimeType": "application/zip"}
        media = MediaFileUpload(zip_created_path, mimetype="application/zip", resumable=True)

        # Upload the file without setting permissions
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get("id")

        # Set the file permissions separately
        permission = {'type': 'anyone', 'role': 'writer'}
        service.permissions().create(fileId=file_id, body=permission).execute()

        # Get the file's webContentLink
        file = service.files().get(fileId=file_id, fields='webContentLink').execute()
        file_url = file.get('webContentLink')

        print(F'File ID: {file_id}')
        print(F'File URL: {file_url}')
        return ZipInfo(zip_id=file_id, url=file_url)


    except HttpError as error:
        print(F'An error occurred: {error}')
        return

def delete_zip(zip_id, credential_path):
    cred = get_token(credential_path)
    try:
        service = build("drive", 'v3', credentials=cred)
        service.files().delete(fileId=zip_id).execute()
        print(F'Zip file with ID {zip_id} was deleted from Drive.')
        return True

    except HttpError as error:
        print(F'An error occurred: {error}')

class ZipInfo(NamedTuple):
    url: str
    zip_id: str
