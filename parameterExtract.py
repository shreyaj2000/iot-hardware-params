#!/usr/bin/env python
import psutil
import tracemalloc
import os
import datetime
 

def main():
    tracemalloc.start()
    # print ('Nr. of processes: ' +str(get_process_count()))
    # print ('Nr. of connections: ' +str(get_connections()))
    # print ('IP-address: ' +get_ipaddress())
    # print ('CPU speed: ' +str(get_cpu_speed()))
    # sending the uptime command as an argument to popen()
    print(os.popen('uptime -p').read()[:-1])
    # Sensor temperatures
    print(psutil.sensors_temperatures())
    # Boot Time
    print('boot time: '+ str(datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")))
    
    '''
    CPU Information
    '''
    # CPU utilization as a percentage. percentage of processor being used
    print('cpu %:' + str(psutil.cpu_percent()))
    # Number of logical CPUs in the system
    print('cpu count:' + str(psutil.cpu_count()))
    # CPU statistics (monitoring system call  for malware attack)
    print(psutil.cpu_stats())
    # CPU Frequency/clock speed
    print('cpu freq:' + str(psutil.cpu_freq()))
    # average system load over the last 1, 5 and 15 minutes
    # Processes which are using the CPU or waiting to use the CPU
    print('system load:' + str([x / psutil.cpu_count() * 100 for x in psutil.getloadavg()]))
    
    '''
    Memory Information
    '''
    # Total physical memory in gb
    print('total physical memory:' + str(psutil.virtual_memory().total/10**9)+ ' GB')
    # Memory currently in use, and so it is in RAM
    print('RAM usage:', str(psutil.virtual_memory().active/10**6)+ ' MB')
    # you can calculate percentage of available memory
    print('memory % available:' + str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))
    # you can have the percentage of used RAM
    print('memory % used:', str(psutil.virtual_memory().percent))
    
    '''
    Disk Usage
    '''
    # hard drive storage. How much percentage of storage (HDD, SSD) being used.
    print(psutil.disk_usage('/'))
    
    '''
    Network Peformance
    '''
    # Bytes sent
    print('number of bytes sent:' + str(psutil.net_io_counters().bytes_sent))
    # Bytes received
    print('number of bytes received:' + str(psutil.net_io_counters().bytes_recv))
    # Packets sent
    print('number of bytes sent:' + str(psutil.net_io_counters().packets_sent))
    # Packets received
    print('number of bytes sent:' + str(psutil.net_io_counters().packets_recv))
    # Info about each Network Interface Card
    print(psutil.net_if_stats())
    
    

    print('---------------------------')
    current, peak = tracemalloc.get_traced_memory()
    print(f"Program memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()

if __name__=="__main__":
    main()