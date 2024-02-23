import datetime
import logging
import os
import time

from google_drive_service_client import GoogleDriveServiceClient

logging.basicConfig(level=logging.INFO)

PUBLIC_ACCESS_PERMISSIONS = ['anyoneWithLink']
CHECK_NEW_FILES_FREQUENCY = 10  # in seconds
LAST_CHECK_TIMESTAMP_PATH = 'audit/last_check_timestamp.txt'


class GoogleDriveSecurityChecker:

    def __init__(self, service_client: GoogleDriveServiceClient = None):
        self.service_client = service_client
        if service_client is None:
            self.service_client: GoogleDriveServiceClient = GoogleDriveServiceClient()

    @staticmethod
    def get_last_check_timestamp():
        if os.path.exists(LAST_CHECK_TIMESTAMP_PATH):
            return GoogleDriveSecurityChecker.load_last_check_timestamp()

    @staticmethod
    def save_now_as_last_check_timestamp():
        with open(LAST_CHECK_TIMESTAMP_PATH, 'w') as file:
            file.write(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

    @staticmethod
    def load_last_check_timestamp():
        with open(LAST_CHECK_TIMESTAMP_PATH, 'r') as file:
            datetime_str = file.read().strip()
            return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')

    def get_files_list(self):
        return self.service_client.get_files_list()

    @staticmethod
    def extract_permissions_of_public_access(file):
        permissions_indicate_public_access = []
        publicly_accessible = False
        logging.info(f'Checking file {file["name"]} permissions... ')
        for permission in file['permissions']:
            if 'id' in permission and permission['id'] in PUBLIC_ACCESS_PERMISSIONS:
                permissions_indicate_public_access.append(permission['id'])
                publicly_accessible = True

        if publicly_accessible:
            logging.info(f'File {file["name"]} found as public to anyone with link')
        else:
            logging.info(f'File {file["name"]} can\'t be accessed publicly')

        return publicly_accessible, permissions_indicate_public_access

    def get_change_list(self):
        logging.info('Checking for new changes...')
        change_list = self.service_client.get_change_list()
        changes_number = len(change_list['changes'])
        if changes_number > 0:
            logging.info(f'{changes_number} changes')
        else:
            logging.info('No changes')

        return change_list['changes']

    @staticmethod
    def extract_changed_file_ids(change_list):
        changed_file_ids = []
        for change in change_list:
            if change['changeType'] == 'file' and change['kind'] == 'drive#change' and 'folder' not in change['file']['mimeType']:
                changed_file_ids.append(change['file']['id'])

        logging.info(f'{len(changed_file_ids)} files were changed')

        return changed_file_ids

    @staticmethod
    def is_file_created_since_last_check_time(file, last_check_timestamp):
        file_created_at = datetime.datetime.strptime(file['createdTime'], '%Y-%m-%dT%H:%M:%S.%fZ')

        return last_check_timestamp < file_created_at

    def start_monitoring(self):
        logging.info('Start monitoring you Google Drive')
        while True:
            last_check_timestamp = self.get_last_check_timestamp()
            logging.debug(f'last timestamp was {last_check_timestamp}')
            try:
                change_list = self.get_change_list()
                changed_files_ids = self.extract_changed_file_ids(change_list)

                for file_id in changed_files_ids:
                    publicly_access_permissions = []
                    file = self.service_client.get_file(file_id=file_id)
                    if self.is_file_created_since_last_check_time(file, last_check_timestamp):
                        logging.info(f"{file['name']} ({file['id']}) - added since the last check time")
                        publicly_accessible, publicly_access_permissions = self.extract_permissions_of_public_access(
                            file=file)
                        if publicly_accessible:
                            self.service_client.change_permissions_to_private(
                                file=file, publicly_access_permissions=publicly_access_permissions)

            except Exception as error:
                logging.error(f"An error occurred: {error}")

            logging.info(f'Sleeping for {CHECK_NEW_FILES_FREQUENCY} seconds...')
            self.save_now_as_last_check_timestamp()
            time.sleep(CHECK_NEW_FILES_FREQUENCY)


if __name__ == "__main__":
    google_drive_service_client = GoogleDriveServiceClient()
    google_drive_security_checker = GoogleDriveSecurityChecker(service_client=google_drive_service_client)
    google_drive_security_checker.start_monitoring()
