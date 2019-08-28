#!/usr/bin/python
import requests
import json
import subprocess
import os


def needs_update():
    # Check drive vs local to see if there are any differences that need synced.
    # We will always exclude ".metadata.json" as this is really printer specific.
    try:
        print("Checking to see if files are in sync.")
        subprocess.check_call(['rclone', 'check', g_drive, local_drive, '--exclude', exclude1, '--exclude', exclude2])
        update_needed = False
        print("Files ARE in sync.")
    except subprocess.CalledProcessError:
        update_needed = True
        print("Files are NOT in sync.")
    return update_needed


def safe_to_sync():
    # Make sure the printer isn't running.
    r_data = requests.get('http://localhost/api/printer', proxies=g_proxys)
    if r_data.status_code == 409:
        # 403 means octoprint is not even connected to the printer. Safe to update files
        print("Printer is Offline (http 409).")
        return True
    if r_data.status_code == 200:
        print("Printer is Online (http 200).")
        # Convert string to json
        j_data = json.loads(r_data.text)
        # OK now get weather we are printing or not
        if j_data['state']['text'] == 'Operational':
            print('Printer is in an "Operational" state.')
            return True
        else:
            print('Printer is NOT in an "Operational" state.')
            return False


def sync():
    print("Sync Happening")
    os.system('rclone sync {} {} --exclude {} --exclude {}'.format(g_drive, local_drive, exclude1, exclude2))
    print("Sync Complete")


if __name__ == '__main__':
    g_drive = 'drive:/'
    local_drive = '/home/pi/.octoprint/uploads/'
    exclude1 = '*.json'
    exclude2 = 'oneoff/'
    http_proxy = "http://127.0.0.1:3128"
    g_proxys = {
    }
    if safe_to_sync():
        print("Safe to Sync = True")
        if needs_update():
            print("Files are out of sync.")
            sync()
