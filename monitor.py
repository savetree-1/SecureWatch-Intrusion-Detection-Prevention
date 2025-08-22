import os
import time
import psutil



import logging

def monitor_network_connections(interval=5, log_file="./logs/network_connections_log.txt"):
    """Monitor network connections and log new connections."""
    previous_connections = set()
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

    while True:
        current_connections = set()
        for connection in psutil.net_connections(kind="inet"):
            laddr = connection.laddr
            raddr = connection.raddr
            status = connection.status
            if raddr:
                current_connections.add((laddr, raddr, status))

        new_connections = current_connections - previous_connections
        for connection in new_connections:
            laddr, raddr, status = connection
            msg = f"Network: {laddr} -> {raddr} - {status}"
            logging.info(msg)

        previous_connections = current_connections
        time.sleep(interval)



def monitor_system_processes(interval=60, cpu_threshold=80, mem_threshold=80, log_file="./logs/processes_log.txt"):
    """Monitor system processes and log those exceeding CPU or memory thresholds."""
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')
    while True:
        for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            pid = process.info["pid"]
            name = process.info["name"]
            cpu_percent = process.info["cpu_percent"]
            mem_percent = process.info["memory_percent"]

            if cpu_percent > cpu_threshold or mem_percent > mem_threshold:
                msg = f"Process: {name} (PID: {pid}) - CPU: {cpu_percent}%, MEM: {mem_percent}%"
                logging.warning(msg)
        time.sleep(interval)