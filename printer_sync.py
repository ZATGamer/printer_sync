#!/usr/bin/python
import requests
import json
import subprocess
import os
import datetime


def stage_needs_update():
    # Check drive vs local to see if there are any differences that need synced.
    # We will always exclude ".metadata.json" as this is really printer specific.
    try:
        print("Checking to see if files are in sync.")
        subprocess.check_call(['rclone', 'check', g_drive, local_stage])
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
            print('Printer is NOT in an "Operational" state.\n'
                  'This means that printer should be printing.')
            return False


def sync_cloud_to_stage():
    print("Sync from cloud to stage Happening")
    os.system('rclone sync {} {}'.format(g_drive, local_stage))
    print("Sync Complete")


def sync_stage_to_production():
    print("Sync From stage to production Happening")
    os.system(
        'rclone sync {} {} --exclude {} --exclude {} --exclude {}'.format(local_stage, local_production, exclude1, exclude2, exclude3))
    print("Sync Complete")


def check_production_to_stage():
    pass
    #os.walk()


def pre_check():
    if not safe_to_sync():
        print('Printer is Printing. Not Continuing.')
        exit(1)
    # Make sure This is the only instance of the script running.
    if not os.path.exists('/tmp/printer_sync.lock'):
        # Create lock file:
        print("Creating Lock File.")
        with open('/tmp/printer_sync.lock', 'w') as lock:
            lock.write('{}'.format(datetime.datetime.now()))
    else:
        print('Lock File exists.... Exiting...')
        exit(1)

    # Make sure stage folder exists
    if not os.path.exists(local_stage):
        os.mkdir(local_stage)


def post_check():
    # Remove Lock file
    print("Removing Lock File")
    os.remove('/tmp/printer_sync.lock')


def main():
    pre_check()
    # Compare staging to Google
    if stage_needs_update():
        # Sync Google to stage if needed
        sync_cloud_to_stage()
        # Set a sync needed flag to true
        with open(sync_flag, 'a'):
            os.utime(sync_flag, None)

    # Check sync needed flag
    if os.path.exists(sync_flag):
        # Check if printer is printing
        if safe_to_sync():
            # rclone sync staging to production
            sync_stage_to_production()
            # Clear sync needed flag
            os.remove(sync_flag)

    post_check()


if __name__ == '__main__':
    g_drive = 'drive:/'
    stage = 'stage:/'
    local_stage = '/tmp/stage/'
    local_production = '/home/pi/.octoprint/uploads/'
    sync_flag = '/tmp/sync_needed'
    exclude1 = '*.json'
    exclude2 = 'oneoff/'
    exclude3 = '*.ini'
    http_proxy = "http://127.0.0.1:3128"
    g_proxys = {
    }
    main()
