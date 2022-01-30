#!/usr/bin/env python
import psutil
import tracemalloc
import os
import datetime
from uuid import getnode as get_mac

try:
    from jtop import jtop 
except:
    print('Unable to import jtop')

try:
    import RPi.GPIO as GPIO
except:
    print('Unable to import RPi.GPIO')
 

def main():
    tracemalloc.start()

    with jtop() as jetson:
        print('================ Jetson Info =================')
        print("GPU freq: " + str(jetson.gpu["frq"]))
        for cpu, stats in jetson.cpu.items():
            print("CPU freq: " + str(stats["frq"]))
            break
        print("GPU temp: " + str(jetson.temperature["GPU"]))

    print('============== Device Info ===============')
    print("MAC Address: " + str(get_mac()))
    print("Operating System: " + os.uname().sysname)
    print("Device Machine: " + os.uname().machine)

    print('================ Boot Info =================')
    # sending the uptime command as an argument to popen()
    print(os.popen('uptime -p').read()[:-1])
    # Boot Time
    print('boot time: '+ str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")))
    
    print('================ CPU Info =================')
    # Sensor temperatures
    sensors_temperatures = psutil.sensors_temperatures(fahrenheit=False)
    for name, entries in sensors_temperatures.items():
        print(name)
        for entry in entries:
            print(f'Current CPU Temp: ' + str(entry.current))
    # CPU utilization as a percentage. percentage of processor being used
    print('cpu %: ' + str(psutil.cpu_percent()))
    # Number of logical CPUs in the system
    print('cpu count: ' + str(psutil.cpu_count()))
    # CPU statistics (monitoring system call  for malware attack)
    print('System calls: ' + str(psutil.cpu_stats().syscalls))
    # CPU Frequency/clock speed
    print(f"Current CPU Frequency: {psutil.cpu_freq().current:.2f}Mhz")
    print(f"Minimum CPU Frequency: {psutil.cpu_freq().min:.2f}Mhz")
    print(f"Maximum CPU Frequency: {psutil.cpu_freq().max:.2f}Mhz")
    # average system load over the last 1, 5 and 15 minutes
    # Processes which are using the CPU or waiting to use the CPU
    print('system load:' + str([x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]))
    
    print('=============== Memory Info ================')
    # Total physical memory in gb
    print('total physical memory:' + str(psutil.virtual_memory().total/10**9)+ ' GB')
    # Memory currently in use, and so it is in RAM
    print('RAM usage:', str(psutil.virtual_memory().active/10**6)+ ' MB')
    # you can calculate percentage of available memory
    print('memory % available:' + str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))
    # you can have the percentage of used RAM
    print('memory % used:', str(psutil.virtual_memory().percent))
    
    print('================ Disk Usage =================')
    # hard drive storage. How much percentage of storage (HDD, SSD) being used.
    print('disk usage %: ' + str(psutil.disk_usage('/').percent))
    
    print('============ Network Performance ==============')
    # Bytes sent
    print('number of bytes sent: ' + str(psutil.net_io_counters().bytes_sent))
    # Bytes received
    print('number of bytes received: ' + str(psutil.net_io_counters().bytes_recv))
    # Packets sent
    print('number of packets sent: ' + str(psutil.net_io_counters().packets_sent))
    # Packets received
    print('number of packets received: ' + str(psutil.net_io_counters().packets_recv))
    # Info about each Network Interface Card
    print(psutil.net_if_stats())
    
    

    print('----------------------------------------------')
    current, peak = tracemalloc.get_traced_memory()
    print(f"Program memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    print(f'{peak *100 / psutil.virtual_memory().active:.3f} % of used RAM')
    tracemalloc.stop()

if __name__=="__main__":
    main()