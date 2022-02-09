#!/usr/bin/env python
import psutil
import tracemalloc
import os
from os.path import exists
import datetime
from uuid import getnode as get_mac
import time
import csv
import re
import socket 

JTOP_IMPORT = False
RPI_IMPORT = False

try:
    from jtop import jtop 
    JTOP_IMPORT = True
except:
    print('Unable to import jtop')

try:
    import RPi.GPIO as GPIO
    RPI_IMPORT = True
except:
    print('Unable to import RPi.GPIO')


def print_data():
    if JTOP_IMPORT:
        with jtop() as jetson:
            print('================ Jetson Info =================')
            print("GPU freq: " + str(jetson.gpu["frq"]))
            for cpu, stats in jetson.cpu.items():
                print("CPU freq: " + str(stats["frq"]))
                break
            print("GPU temp: " + str(jetson.temperature["GPU"]))
    elif RPI_IMPORT:
        print('================= RPI Info ==================')
        print(os.popen('vcgencmd measure_volts').read()[:-1])
        print(os.popen('vcgencmd get_throttled').read()[:-1])
    print('============== Device Info ===============')
    print("MAC Address: " + str(get_mac()))
    print("Operating System: " + os.uname().sysname)
    print("Device Machine: " + os.uname().machine)
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Computer Name: " + hostname)    
    print("Computer IP Address: " + IPAddr) 

    print('================ Boot Info =================')
    # sending the uptime command as an argument to popen()
    print(os.popen('uptime -p').read()[:-1])
    # Boot Time
    print('boot time: '+ str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")))
    
    print('================ CPU Info =================')
    # Sensor temperatures
    try:
        sensors_temperatures = psutil.sensors_temperatures(fahrenheit=False)
        for name, entries in sensors_temperatures.items():
            print(name)
            for entry in entries:
                print(f'Current CPU Temp: ' + str(entry.current))
    except:
        print("Cannot print CPU temp")
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
    print('total disk space: ' + str(psutil.disk_usage('/').total/10**9)+' GB')
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
    # print(psutil.net_if_stats())


def add_data_to_csv():
    data = []
    data.append(datetime.datetime.now())
    if JTOP_IMPORT:
        with jtop() as jetson:
            data.append(jetson.gpu["frq"])
            for cpu, stats in jetson.cpu.items():
                data.append(stats["frq"])
                break
            data.append(jetson.temperature["GPU"])
    elif RPI_IMPORT:
        data.append(float(re.sub("[^\d\.]", "", os.popen('vcgencmd measure_volts').read()[:-1])))
        data.append(re.search(r'0(\w+)', os.popen('vcgencmd get_throttled').read()[:-1]).group())
    data.append(get_mac())
    data.append(os.uname().sysname)
    data.append(os.uname().machine)
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    data.append(hostname)    
    data.append(IPAddr)
    data.append(os.popen('uptime -p').read()[:-1])
    data.append(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"))
    try:
        sensors_temperatures = psutil.sensors_temperatures(fahrenheit=False)
        for name, entries in sensors_temperatures.items():
            for entry in entries:
                data.append(entry.current)
    except:
        print("Cannot print CPU temp")
    data.append(psutil.cpu_percent())
    data.append(psutil.cpu_count())
    data.append(psutil.cpu_stats().syscalls)
    data.append(psutil.cpu_freq().current)
    data.append(psutil.cpu_freq().min)
    data.append(psutil.cpu_freq().max)
    data.append(psutil.getloadavg()[0]/psutil.cpu_count() * 100)
    data.append(psutil.getloadavg()[1]/psutil.cpu_count() * 100)
    data.append(psutil.getloadavg()[2]/psutil.cpu_count() * 100)
    data.append(psutil.virtual_memory().total/10**9)
    data.append(psutil.virtual_memory().active/10**6)
    data.append(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
    data.append(psutil.virtual_memory().percent)
    data.append(psutil.disk_usage('/').percent)
    data.append(psutil.disk_usage('/').total/10**9)
    data.append(psutil.net_io_counters().bytes_sent)
    data.append(psutil.net_io_counters().bytes_recv)
    data.append(psutil.net_io_counters().packets_sent)
    data.append(psutil.net_io_counters().packets_recv)
    # data.append(psutil.net_if_stats())

    return data



def main():
    # header = ['name', 'area', 'country_code2', 'country_code3']
    # Month abbreviation, day and year  
    today = datetime.date.today()
    date_formatted = today.strftime("%b_%d_%Y")
    file_name = 'params_' + os.uname().machine + '_' + date_formatted + '.csv'
    file_exists = exists(file_name)
    if file_exists:
        append_write = 'a' # append if already exists
    else:
        append_write = 'w' # make a new file if not
    with open(file_name, append_write, encoding='UTF8') as f:
        writer = csv.writer(f)
        # write the header
        # if not file_exists:
            # writer.writerow(header)
        while True:
            start = datetime.datetime.now()
            tracemalloc.start()

            #print_data()

            data = add_data_to_csv()
            
            # write the data
            writer.writerow(data)

            print('----------------------------------------------')
            current, peak = tracemalloc.get_traced_memory()
            #print(f"Program memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
            #print(f'{peak *100 / psutil.virtual_memory().active:.3f} % of used RAM')
            tracemalloc.stop()
            print(f'Time taken: {(datetime.datetime.now()-start).microseconds} microseconds')
            time.sleep(60)

if __name__=="__main__":
    main()