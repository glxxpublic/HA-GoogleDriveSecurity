import logging
import os
import traceback
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# TODO check if I can do that with lower permissions
SCOPES = ["https://www.googleapis.com/auth/drive"]

LAST_PAGE_TOKEN_PATH = os.path.join('audit', 'last_page_token.txt')


class GoogleDriveServiceClient:

    def __init__(self):
        self.creds = None
        self.service_client = None
        self.init_google_drive_service_client()
        self.last_page_token = self.get_page_token()

    def save_page_token(self, changes_list):
        if 'nextPageToken' in changes_list:
            self.last_page_token = changes_list['nextPageToken']
        elif 'newStartPageToken' in changes_list:
            self.last_page_token = changes_list['newStartPageToken']
        with open(LAST_PAGE_TOKEN_PATH, 'w') as last_page_token_file:
            last_page_token_file.write(self.last_page_token)

    def get_start_page_token(self):
        return self.service_client.changes().getStartPageToken().execute()['startPageToken']

    def load_last_page_token(self):
        with open(LAST_PAGE_TOKEN_PATH, 'r') as last_page_token_file:
            self.last_page_token = last_page_token_file.read()

        return self.last_page_token

    def get_page_token(self):
        if os.path.exists(LAST_PAGE_TOKEN_PATH):
            page_token = self.load_last_page_token()
        else:
            page_token = self.get_start_page_token()

        return page_token

    def init_google_drive_service_client(self):
        assert os.path.exists(os.path.join('config', 'credentials.json')), \
            "You should get you project credentials. please follow readme and get it here: " \
            "https://console.cloud.google.com/apis/credentials"
        self.creds = None
        if os.path.exists(os.path.join('config', 'token.json')):
            self.creds = Credentials.from_authorized_user_file(os.path.join('config', 'token.json'), SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(os.path.join('config', 'credentials.json'), SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(os.path.join('config','token.json'), "w") as token:
                token.write(self.creds.to_json())

        self.service_client = build("drive", "v3", credentials=self.creds)

    def get_change_list(self):
        changes_list = self.service_client.changes().list(pageToken=self.last_page_token).execute()
        self.save_page_token(changes_list=changes_list)

        return changes_list

    def change_permissions_to_private(self, file, publicly_access_permissions):
        print(f'Changing file {file["name"]} to private')
        for permission_id in publicly_access_permissions:
            try:
                logging.info(f'Deleting permissions {permission_id} for file {file["name"]}...')
                a = self.service_client.permissions().delete(fileId=file['id'], permissionId=permission_id).execute()
                logging.info('Done')
            except Exception as e:
                traceback.print_exc()

    def get_file(self, file_id):
        return self.service_client.files().get(fileId=file_id, fields="id, name, permissions, createdTime")\
            .execute()
