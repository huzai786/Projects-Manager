import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata", "https://www.googleapis.com/auth/drive.readonly",
          "https://www.googleapis.com/auth/drive.metadata.readonly"]

root_folder = "google_drive"

def get_token(file="credentials.json"):
    file_path = os.path.join(root_folder, file)
    if not os.path.exists(os.path.join(root_folder, file)):
        raise Exception(f"{file_path} doesn't exists!")

    cred = None
    token_file_path = os.path.join(root_folder, "token.json")
    if os.path.exists(token_file_path):
        cred = Credentials.from_authorized_user_file(token_file_path, SCOPES)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                file_path, SCOPES
            )
            cred = flow.run_local_server(port=0)
        with open(token_file_path, 'w') as file:
            file.write(cred.to_json())
        return Credentials.from_authorized_user_file(token_file_path, SCOPES)

    return cred


def upload_zip(file_path):
    cred = get_token()
    name = os.path.basename(file_path)

    try:
        service = build("drive", 'v3', cred)
        file_metadata = {"name": name, "mimeType": "application/zip"}
        media = MediaFileUpload(file_path, mimetype="application/zip", resumable=True)

        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(f'File ID: {file.get("id")}')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return


















