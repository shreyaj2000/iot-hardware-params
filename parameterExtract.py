#!/usr/bin/env python
import psutil
import tracemalloc
import os
from os.path import exists
import datetime
import getmac
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

def get_list_of_process_sorted_by_memory():
    '''
    Get list of running process sorted by Memory Usage
    '''
    processes = []
    # Iterate over the list
    for proc in psutil.process_iter():
       try:
           # Fetch process details as dict
           pinfo = proc.as_dict(attrs=['memory_percent','name', 'username', 'pid'])
           # Append dict to list
           processes.append(pinfo);
       except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
           pass
    # Sort list of dict by key vms i.e. memory usage
    processes = sorted(processes, key=lambda process: process['memory_percent'], reverse=True)
    
    grouped_res = {}
    
        
    for row in processes[:10] :
        if row['name'] in grouped_res:
            grouped_res[row['name']] += float(row['memory_percent'])
        else:
            grouped_res[row['name']] = float(row['memory_percent'])
            
    return grouped_res

def get_list_of_process_sorted_by_cpu():
    output = os.popen('ps -Ao pcpu,comm,user,pid k-pcpu | head -10')
    res = []
    first_line = True
    for line in output.readlines():
        term = ''
        row = []
        line = line.rstrip('\n')
        if first_line:
            first_line = False
            continue
        for c in line:
            if c == ' ' and term!='':
                row.append(term)
                term=''
            elif c != ' ':
                term+=c
        row.append(term)
        res.append(row)
    
    grouped_res = {}
    for row in res:
        if row[1] in grouped_res:
            grouped_res[row[1]] += float(row[0])
        else:
            grouped_res[row[1]] = float(row[0])
            
    grouped_res = sorted(grouped_res.items(), key=lambda x:x[1], reverse=True)
    grouped_res = dict(grouped_res)
    
    return grouped_res

def get_model_pins(argument):
    #Detect Raspberry Pi model and number of GPIO pins
    switcher = {
        "0002": ("Model B Revision 1.0 256Mb",17),
        "0003": ("Model B Revision 1.0 + ECN0001 256Mb",17),
        "0004": ("Model B Revision 2.0 256Mb",17),
        "0005": ("Model B Revision 2.0 256Mb",17),
        "0006": ("Model B Revision 2.0 256Mb",17),
        "0007": ("Model A 256Mb",17),
        "0008": ("Model A 256Mb",17),
        "0009": ("Model A 256Mb",17),
        "000d": ("Model B Revision 2.0 512Mb",17),
        "000e": ("Model B Revision 2.0 512Mb",17),
        "000f": ("Model B Revision 2.0 512Mb",17),
        "0010": ("Model B+ 512Mb",26),
        "0012": ("Model A+ 256Mb",26),
        "0013": ("Model B+ 512Mb",26),
        "13": ("Model B+ 512Mb",26),  # https://github.com/kgbplus/gpiotest/issues/7
        "0015": ("Model A+ 256/512Mb",26),
        "a01040": ("2 Model B Revision 1.0 1Gb",26),
        "a01041": ("2 Model B Revision 1.1 1Gb",26),
        "a21041": ("2 Model B Revision 1.1 1Gb",26),
        "a22042": ("2 Model B (with BCM2837) 1Gb",26),
        "900021": ("Model A+ 512Mb",26),
        "900032": ("Model B+ 512Mb",26),
        "900092": ("Zero Revision 1.2 512Mb",26),
        "900093": ("Zero Revision 1.3 512Mb",26),
        "920093": ("Zero Revision 1.3 512Mb",26),
        "9000c1": ("Zero W Revision 1.1 512Mb",26),
        "a02082": ("3 Model B 1Gb",26),
        "a22082": ("3 Model B 1Gb",26),
        "a32082": ("3 Model B 1Gb",26),
        "a020d3": ("3 Model B+ 1Gb",26),
        "9020e0": ("3 Model A+ 512Mb",26),
        "a03111": ("4 Model B 1Gb",26),
        "b03111": ("4 Model B 2Gb",26),
        "b03112": ("4 Model B 2Gb",26),
        "bo3114": ("4 Model B 2Gb",26),
        "c03111": ("4 Model B 4Gb",26),
        "c03112": ("4 Model B 4Gb",26),
        "c03114": ("4 Model B 4Gb",26),
        "d03114": ("4 Model B 8Gb",26),
        "c03130": ("Pi 400 4Gb",26),
        "b03140": ("Compute Module 4 2Gb",26),
    }
    return switcher.get(argument, ("not supported",0))


def initGpio(gpio_ch, firstrun=0):
    all_pin_states = ''

    #Init GPIO
    if not firstrun:
        GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(0)


    #Init GPIO pins, save states etc.
    for i,channel in enumerate(gpio_ch):
        GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
        all_pin_states += str(GPIO.input(channel)) # Primary state
            
    return all_pin_states


def get_gpio_pins_status(gpio_num):
    #gpio_ch - array of GPIO lines numbers
    if (gpio_num == 17):
        gpio_ch = [0,1,4,7,8,9,10,11,14,15,17,18,21,22,23,24,25]
    else:
        gpio_ch = [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

    return(initGpio(gpio_ch,1))

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
        print(os.popen('vcgencmd read_ring_osc').read()[:-1])
        raspi_model = get_model_pins(GPIO.RPI_INFO['REVISION'])
        print(f'RPI Model: {raspi_model[0]}')
        print('GPIO Pin States: ' + get_gpio_pins_status(raspi_model[1]))
    print('============== Device Info ===============')
    print("MAC Address: " + getmac.get_mac_address())
    print("Operating System: " + os.uname().sysname)
    print("Device Machine: " + os.uname().machine)
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname + ".local")    
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
    # Processes using most CPU%
    print(get_list_of_process_sorted_by_cpu())
    print('=============== Memory Info ================')
    # Total physical memory in gb
    print('total physical memory:' + str(psutil.virtual_memory().total/10**9)+ ' GB')
    # Memory currently in use, and so it is in RAM
    print('RAM usage:', str(psutil.virtual_memory().active/10**6)+ ' MB')
    # you can calculate percentage of available memory
    print('memory % available:' + str(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total))
    # you can have the percentage of used RAM
    print('memory % used:', str(psutil.virtual_memory().percent))
    # Processes using most Memory%
    print(get_list_of_process_sorted_by_memory())
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
        voltage = re.sub("[^\d\.]", "", os.popen('vcgencmd measure_volts').read()[:-1])
        if voltage is not None:
            data.append(float(voltage))
        throttled_state = re.search(r'0(\w+)', os.popen('vcgencmd get_throttled').read()[:-1])
        if throttled_state is not None:
            data.append(throttled_state.group())
        ring_oscillation = re.search(r'(?<==).*(?=M)', os.popen('vcgencmd read_ring_osc').read()[:-1])
        if ring_oscillation is not None:
            data.append(ring_oscillation.group())
        raspi_model = get_model_pins(GPIO.RPI_INFO['REVISION'])
        data.append(raspi_model[0])
        data.append(get_gpio_pins_status(raspi_model[1]))
    data.append(getmac.get_mac_address())
    data.append(os.uname().sysname)
    data.append(os.uname().machine)
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname + ".local")    
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
    data.append(get_list_of_process_sorted_by_cpu())
    data.append(psutil.virtual_memory().total/10**9)
    data.append(psutil.virtual_memory().active/10**6)
    data.append(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total)
    data.append(psutil.virtual_memory().percent)
    data.append(get_list_of_process_sorted_by_memory())
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
            print(f"Program memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB")
            print(f'{peak *100 / psutil.virtual_memory().active:.3f} % of used RAM')
            tracemalloc.stop()
            print(f'Time taken: {(datetime.datetime.now()-start).microseconds} microseconds')
            print('----------------------------------------------')
            time.sleep(60)

if __name__=="__main__":
    main()