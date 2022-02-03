import datetime
import xlsxwriter
import csv

today = datetime.date.today()
date_formatted = today.strftime("%b_%d_%Y")

# Create a workbook and add a worksheet.
xlsx_file_name = 'params_' + date_formatted + '.xlsx'
workbook = xlsxwriter.Workbook(xlsx_file_name)
worksheet = workbook.add_worksheet()

csv_file_name = 'params_' + date_formatted + '.csv'


my_list = ['MAC_Address', 'Operating_System', 'Device_Machine', 'Uptime', 'Boottime',
'CPU%', 'CPU_count', 'System_Calls', 'Current_CPU_Freq', 'Min_CPU_Freq', 'Max_CPU_Freq',
'System_Load_Avg_1Min','System_Load_Avg_5Min','System_Load_Avg_15Min', 'Physical_Memory', 'RAM_Usage', 'Memory%_Avaialbe', 'Memory%_Used', 
'Disk_Usage','Number_bytes_sent', 'Number_bytes_received', 'Number_packets_sent',
'Number_packets_received']

for col_num, data in enumerate(my_list):
    worksheet.write(0, col_num, data)

# Add csv file
with open(csv_file_name, 'rt', encoding='utf8') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
        	if r == 0:
        		continue
        	for c, col in enumerate(row):
        		worksheet.write(r, c, col)

workbook.close()