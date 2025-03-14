import threading
import psutil
import GPUtil
import time
from tabulate import tabulate

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current  # Get first core temp
    except AttributeError:
        return "Not Available"
    return "Not Available"

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.total, mem.used, mem.percent

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.total, disk.used, disk.percent

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    if not gpus:
        return "No GPU found"
    
    gpu_data = []
    for gpu in gpus:
        gpu_data.append({
            "GPU Name": gpu.name,
            "Usage (%)": gpu.load * 100,
            "Memory Used (MB)": gpu.memoryUsed,
            "Memory Free (MB)": gpu.memoryFree,
            "Temperature (°C)": gpu.temperature
        })
    return gpu_data

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return battery.percent, battery.power_plugged
    return "No Battery Info"

def get_network_usage():
    net = psutil.net_io_counters()
    return net.bytes_sent, net.bytes_recv

def get_running_processes():
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        process_list.append([
            proc.info['pid'],
            proc.info['name'],
            proc.info['cpu_percent'],
            proc.info['memory_percent']
        ])
    return process_list[:10]  # Get top 10 processes

def get_fan_speed():
    try:
        fans = psutil.sensors_fans()
        if fans:
            return fans
    except AttributeError:
        return "Not Available"
    return "Not Available"

def monitor_system():
    while True:
        cpu = get_cpu_usage()
        cpu_temp = get_cpu_temperature()
        total_mem, used_mem, mem_percent = get_memory_usage()
        total_disk, used_disk, disk_percent = get_disk_usage()
        gpu = get_gpu_usage()
        battery = get_battery_status()
        sent, received = get_network_usage()
        processes = get_running_processes()
        fan_speed = get_fan_speed()

        data = [
            ["CPU Usage (%)", cpu],
            ["CPU Temperature (°C)", cpu_temp],
            ["Memory Usage (%)", mem_percent],
            ["Disk Usage (%)", disk_percent],
            ["Network Sent (MB)", round(sent / (1024 * 1024), 2)],
            ["Network Received (MB)", round(received / (1024 * 1024), 2)],
            ["Fan Speed", fan_speed]
        ]

        if isinstance(gpu, list):
            for g in gpu:
                data.append([g["GPU Name"], f"{g['Usage (%)']}%"])
                data.append(["GPU Temperature (°C)", g["Temperature (°C)"]])
        
        if isinstance(battery, tuple):
            data.append(["Battery (%)", battery[0]])
            data.append(["Charging", "Yes" if battery[1] else "No"])

        print("\nSystem Monitoring Report:")
        print(tabulate(data, headers=["Metric", "Value"], tablefmt="grid"))

        print("\nTop Running Processes:")
        print(tabulate(processes, headers=["PID", "Process Name", "CPU (%)", "Memory (%)"], tablefmt="grid"))

        time.sleep(3)

# Run in a separate thread
monitor_thread = threading.Thread(target=monitor_system, daemon=True)
monitor_thread.start()

# Simulating main program (replace this with your actual logic)
while True:
    print("Main program running... (Press CTRL+C to stop)")
    time.sleep(10)
