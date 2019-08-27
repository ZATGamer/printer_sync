import requests
import json
import subprocess



def needs_update():
    # Check drive vs local to see if there are any differences that need synced.
    # We will always exclude ".metadata.json" as this is really printer specific.
    print subprocess.check_call('rclone check drive:/ /home/pi/test/')
    return True


def safe_to_sync():
    # Make sure the printer isn't running.
    r_data = requests.get('http://192.168.1.202/api/printer', proxies=g_proxys)
    if r_data.status_code == 409:
        # 403 means octoprint is not even connected to the printer. Safe to update files
        print("got 403")
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
    print("Sync Would Happen")


if __name__ == '__main__':
    http_proxy = "http://127.0.0.1:3128"
    g_proxys = {
        "http": http_proxy
    }
    if safe_to_sync():
        if needs_update():
            sync()
