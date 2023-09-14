from fastapi import FastAPI
import os
import platform
import subprocess

app = FastAPI()

def parse_cpu_info(info):
    cpu_info_dict = {}
    for line in info.splitlines():
        if ":" in line:
            parts = line.split(":")
            key = parts[0].strip()
            value = ":".join(parts[1:]).strip()
            cpu_info_dict[key] = value
    return cpu_info_dict

def get_cpu_usage_percent():
    try:
        mpstat_output = subprocess.check_output(["mpstat", "1", "1"]).decode("utf-8")
        lines = mpstat_output.strip().split("\n")
        for line in lines:
            if "all" in line:
                parts = line.split()
                usage_percent = float(parts[-1])
                return usage_percent
        return None
    except Exception as e:
        print(f"Error getting CPU usage: {e}")
        return None

def parse_memory_info(info):
    info_lines = info.strip().split("\n")
    memory_data = info_lines[1].split()
    memory_dict = {
        "Total": memory_data[0],
        "Used": memory_data[1],
        "Free": memory_data[2],
        "Shared": memory_data[3],
        "Buffer/Cache": memory_data[4],
        "Available": memory_data[5],
    }
    return memory_dict

def parse_disk_info(info):
    info_lines = info.strip().split("\n")
    disk_data = info_lines[1].split()
    disk_dict = {
        "Filesystem": disk_data[0],
        "Size": disk_data[1],
        "Used": disk_data[2],
        "Avail": disk_data[3],
        "Use%": disk_data[4],
        "Mounted On": disk_data[5],
    }
    return disk_dict

@app.get("/system-resources")
async def system_resources():
    system_name = platform.system()
    cpu_info = os.popen("lscpu").read()
    cpu_info_percent = {"Usage%": get_cpu_usage_percent()}
    memory_info = os.popen("free -m").read()
    memory_info = parse_memory_info(memory_info)
    disk_info = os.popen("df -h").read()
    disk_info = parse_disk_info(disk_info)
    system_report = {
        "SystemName": system_name,
        "CPUInfo": parse_cpu_info(cpu_info),
        "CPUInfoPercent": cpu_info_percent,
        "MemoryInfo": memory_info,
        "DiskInfo": disk_info,
    }
    return system_report
