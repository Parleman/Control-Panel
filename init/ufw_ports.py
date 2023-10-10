import re
from fastapi import FastAPI
import os
import platform
import subprocess
import json

app = FastAPI()


@app.get("/status")
def check_ufw_status():
    try:
        result_bytes = subprocess.check_output(["sudo", "ufw", "status", "verbose"], stderr=subprocess.STDOUT)

        result_text = result_bytes.decode('utf-8')

        status_line = result_text.splitlines()[0]
        status = status_line.split(": ")[1].strip()

        status_dict = {"status": status}

        status_json = json.dumps(status_dict)
        return status_json
    except subprocess.CalledProcessError as e:
        # اگر اجرای دستور با خطا مواجه شود، پیام خطا چاپ می‌شود
        error = {'Error text': e}
        return error


def get_open_ports():
    try:
        result_bytes = subprocess.check_output(["sudo", "nmap", "-p", "1-54321", "localhost"], stderr=subprocess.STDOUT,
                                               text=True)
        result_text = result_bytes.strip()

        open_ports = re.findall(r'(\d+)/tcp\s+open', result_text)

        open_ports = [int(port) for port in open_ports]

        port_status_dict = {str(port): "open" for port in open_ports}

        return port_status_dict
    except subprocess.CalledProcessError as e:
        print(f"خطا در دریافت پورت‌های باز: {e}")
        return {}


@app.get("/list")
def get_list_of_ports():
    open_ports_dict = get_open_ports()

    all_ports_dict = {str(port): "closed" for port in range(1, 65536)}
    all_ports_dict.update(open_ports_dict)
    return all_ports_dict
