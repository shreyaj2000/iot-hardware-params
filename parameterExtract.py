#!/usr/bin/env python
import psutil
import tracemalloc
import os
 

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
    # Total physical memory in gb
    print('total physical memory:' + str(psutil.virtual_memory().total/10**9)+ 'GB')
    # Memory currently in use, and so it is in RAM
    print('RAM usage:', str(psutil.virtual_memory().active/10**6)+ 'MB')
    # gives a single float value
    print('cpu %:' + str(psutil.cpu_percent()))
    # you can calculate percentage of available memory
    print('memory % available:' + str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))
    # you can have the percentage of used RAM
    print('memory % used:', str(psutil.virtual_memory()[2]))

    print('---------------------------')
    current, peak = tracemalloc.get_traced_memory()
    print(f"Program memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
    tracemalloc.stop()

if __name__=="__main__":
    main()