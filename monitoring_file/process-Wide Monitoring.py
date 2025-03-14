import psutil

def monitor_system():
    """Monitor all running processes and find the heaviest ones"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        processes.append(proc.info)

    # Sort by CPU & RAM usage
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

    print("\n📌 Top Resource-Consuming Processes:")
    print(f"{'PID':<10}{'Process Name':<25}{'CPU %':<10}{'RAM (MB)':<10}")
    print("=" * 55)

    for process in processes[:10]:  # Show top 10 processes
        print(f"{process['pid']:<10}{process['name']:<25}{process['cpu_percent']:<10.2f}{process['memory_info'].rss / (1024 * 1024):<10.2f}")

monitor_system()
