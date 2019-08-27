#!/usr/bin/python
import requests
import json
import subprocess
import os


def needs_update():
    # Check drive vs local to see if there are any differences that need synced.
    # We will always exclude ".metadata.json" as this is really printer specific.
    try:
        subprocess.check_call(['rclone', 'check', g_drive, local_drive, '--exclude', exclude1, '--exclude', exclude2])
        update_needed = False
    except subprocess.CalledProcessError:
        update_needed = True
    print(update_needed)
    return update_needed


def safe_to_sync():
    # Make sure the printer isn't running.
    r_data = requests.get('http://localhost/api/printer', proxies=g_proxys)
    if r_data.status_code == 409:
        # 403 means octoprint is not even connected to the printer. Safe to update files
        print("got 409")
        return True
    if r_data.status_code == 200:
        print("got 200")
        # Convert string to json
        j_data = json.loads(r_data.text)
        # OK now get weather we are printing or not
        if j_data['state']['text'] == 'Operational':
            return True
        else:
            return False


def sync():
    print("Sync Happening")
    os.system('rclone sync {} {} --exclude {} --exclude {}'.format(g_drive, local_drive, exclude1, exclude2))


if __name__ == '__main__':
    g_drive = 'drive:/'
    local_drive = '/home/pi/.octoprint/uploads/'
    exclude1 = '*.json'
    exclude2 = 'oneoff/'
    http_proxy = "http://127.0.0.1:3128"
    g_proxys = {
    }
    if safe_to_sync():
        if needs_update():
            sync()
