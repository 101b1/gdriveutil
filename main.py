from __future__ import print_function

import io
import mimetypes
import pickle
import os.path
import sys

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']


# Checks if path of downloading source exist
def check_path_tree(path, drive_service):
    path_folders = path.split('/')

    path_folders = path_folders[::-1]
    file_name = path_folders[0]
    last_folder = path_folders[1]
    path_folders.remove(file_name)
    if last_folder == '':
        return True
    response = drive_service.files().list(q='mimeType contains "vnd.google-apps.folder"',
                                          fields='files(id, name, parents)').execute()
    folder_list = response.get('files', [])

    id_map = {}
    parent_map = {}

    for fld in folder_list:
        try:
            parent_map[fld['name']] = fld['parents'][0]
            id_map[fld['id']] = fld['name']
        except KeyError:
            continue

    for i in range(0, len(path_folders)):
        folder = path_folders[i]
        parent = path_folders[i+1]
        if parent == '':
            parent_id = 0
            for idd, name in id_map.items():
                if name == last_folder:
                    parent_id = idd
            resp = drive_service.files().list(q='"%s" in parents' % parent_id, fields='files(id,name)').execute()
            file = resp.get('files', [])[0]
            if file_name == file['name']:
                return True
        elif folder in parent_map.keys() and parent == id_map[parent_map[folder]]:
            continue
        else:
            return False


def download(src_path, dest_path, drive_service):
    try:
        filename = src_path.split('/')[-1]
        response = drive_service.files().list(q='name contains "%s"' % filename, fields='files(id,name)').execute()
        file = response.get('files', [])
        request = drive_service.files().get_media(fileId=file[0]['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with open(dest_path, "wb") as f:
            f.write(fh.getvalue())
    except Exception:
        print("Error! No such file!")


def get_folder(folder_name, service):

    check_response = service.files().list(q='mimeType contains "vnd.google-apps.folder" and name = "%s"' % folder_name,
                                          fields='files(id)').execute()
    return check_response.get('files', [])


def upload(src_path, dest_path, service):
    folder_list = dest_path.split('/')
    filename = folder_list.pop()

    if len(folder_list) == 1 and folder_list[0] == '':
        try:
            file_metadata = {'name': filename}
            media = MediaFileUpload(
                src_path,
                mimetype=mimetypes.MimeTypes().guess_type(filename)[0])
            service.files().create(body=file_metadata,
                                   media_body=media,
                                   fields='id').execute()
            return
        except:
            print("Error uploading a file %s !" % src_path)
            print("Check if tha path is correct.")
            return

    parent_ids = []
    folder_list.remove('')
    for i in range(0, len(folder_list)):
        folder_id = get_folder(folder_list[i], service)

        if not folder_id:
            parent = []
            if i != 0:
                parent = parent_ids[i-1]['id']
            folder_metadata = {'name': folder_list[i],
                               'parents': [parent],
                               'mimeType': 'application/vnd.google-apps.folder'}
            create_folder = service.files().create(body=folder_metadata,
                                                   fields='id').execute()
            folder_id = create_folder.get('id', [])

        parent_ids.append(folder_id[0])

    file_metadata = {'name': filename, 'parents': [parent_ids.pop()['id']]}
    media = MediaFileUpload(
        src_path,
        mimetype=mimetypes.MimeTypes().guess_type(filename)[0])
    service.files().create(body=file_metadata,
                           media_body=media,
                           fields='id').execute()


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    args = sys.argv
    src = args[2]
    dest = args[3]

    if args[1] == 'put':
        upload(src, dest, service)
    elif args[1] == 'get':
        if check_path_tree(src, service):
            download(src, dest, service)
    else:
        print("No such command %s." % args[1])
        print("Type 'put' for upload and 'get' for download.")


if __name__ == '__main__':
    main()
