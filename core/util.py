# encoding=utf-8

import os
import xlsxwriter
from conf.config import config


def create_log_path():
    # create log dir using project started time
    start_time = config['U_PROJECT_START_TIME']
    cur_dir = os.path.join(config['U_PROJECT_DIR'], 'testLogs', start_time)
    if not os.path.exists(cur_dir):
        try:
            os.mkdir(cur_dir)
        except:
            raise IOError('Create current directory failed!')
    config['U_LOG_DIR'] = cur_dir
    print (config['U_LOG_DIR'])

def readTopFile(filename=None):
    # Read data from the given file
    cpu_info = []
    cpu = []
    mem_info = []
    vss = []
    rss = []
    if filename is None:
        filename = os.path.join(config['U_LOG_DIR'], config['U_TOP_LOG_NAME'])
    if os.path.exists(filename):
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if config['G_APP_PACKAGE_NAME'] in line:
                    content = line.strip().split()
                    cpu.append(int(content[4].split('%')[0]))
                    vss.append(int(content[7].split('K')[0]))
                    rss.append(int(content[8].split('K')[0]))
    items = range(1, len(cpu)+1)
    cpu_info.append(items)
    cpu_info.append(cpu)
    config['data']['CPU'] = cpu_info
    mem_info.append(items)
    mem_info.append(vss)
    mem_info.append(rss)
    config['data']['Memory'] = mem_info

def readMeminfoFile(filename=None):
    # Read data from the given file
    memory = []
    uptime = []
    native_pss = []
    native_heap_size = []
    native_heap_alloc = []
    dalvik_pss = []
    dalvik_heap_size = []
    dalvik_heap_alloc = []
    total_pss = []

    activity_info = []
    activities = []

    if filename is None:
        filename = os.path.join(config['U_LOG_DIR'], config['U_MEMINFO_LOG_NAME'])
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                if 'Native Heap:' in line:
                    continue
                if 'Native Heap' in line:
                    content = line.strip().split()
                    native_pss.append(int(content[2]))
                    native_heap_size.append(int(content[6]))
                    native_heap_alloc.append(int(content[7]))
                elif 'Dalvik Heap' in line:
                    content = line.strip().split()
                    dalvik_pss.append(int(content[2]))
                    dalvik_heap_size.append(int(content[6]))
                    dalvik_heap_alloc.append(int(content[7]))
                elif 'TOTAL' in line:
                    content = line.strip().split()
                    total_pss.append(int(content[1]))
                elif 'TOTAL:' in line:
                    continue
                elif 'Activities:' in line:
                    content = line.strip().split('Activities:')[1]
                    activities.append(int(content))
    items = range(1, len(total_pss)+1)
    memory.append(items)
    memory.append(total_pss)
    memory.append(native_pss)
    memory.append(native_heap_size)
    memory.append(native_heap_alloc)
    memory.append(dalvik_pss)
    memory.append(dalvik_heap_size)
    memory.append(dalvik_heap_alloc)
    activity_info.append(items)
    activity_info.append(activities)

    config['data']['MemoryDetail'] = memory
    config['data']['Activities'] = activity_info

def readFlowFile(tcp_send=None, tcp_receive=None):
    # Read data from the given file
    flow_info = []
    if tcp_send is None:
        snd_file = os.path.join(config['U_LOG_DIR'], config['U_FLOWOUT_LOG_NAME'])
    if tcp_receive is None:
        rcv_file = os.path.join(config['U_LOG_DIR'], config['U_FLOWIN_LOG_NAME'])
    tcp_snd = readFile(snd_file)
    tcp_rcv = readFile(rcv_file)
    items = range(1, len(tcp_snd)+1)
    flow_info.append(items)
    flow_info.append(tcp_snd)
    flow_info.append(tcp_rcv)
    config['data']['Flow'] = flow_info

def readFPSFile():
    fps_info = []
    fps_file = os.path.join(config['U_LOG_DIR'], config['U_GFXINFO_LOG_NAME'])
    fps = readFile(fps_file)
    items = range(1, len(fps)+1)
    fps_info.append(items)
    fps_info.append(fps)
    config['data']['FPS'] = fps_info

def readFile(filename):
    info = []
    if os.path.exists(filename):
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                content = line.strip()
                info.append(content)
    return info

def combineTestResult(test_results, test_details):
    # create usage of phone resources after running app
    sheet_list = ['CPU', 'Memory', 'MemoryDetail', 'Activities', 'Flow', 'FPS']
    readTopFile()
    readMeminfoFile()
    readFlowFile()
    readFPSFile()
    filename = 'appPerformance{}.xlsx'.format(config['U_PROJECT_START_TIME'])
    filename = os.path.join(config['U_LOG_DIR'], filename)
    workbook = xlsxwriter.Workbook(filename)

    createTestResult(workbook, 'MonkeyTest Result', test_results, test_details)
    createPhoneSummary(workbook, 'Phone Info Summary')

    for sheet_name in sheet_list:
        createLineChart(workbook, sheet_name, config['data'][sheet_name])
    workbook.close()

def createTestResult(workbook, sheet_name, test_results, test_details):
    # Test Report Summary
    worksheet = workbook.add_worksheet(sheet_name)
    merge_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': '#cccccc',
    })
    bold = workbook.add_format({'bold': 1, 'border': 1})
    data_format = workbook.add_format({'border': 1})
    worksheet.merge_range('A1:F1', sheet_name+config['U_PROJECT_START_TIME'], merge_format)
    worksheet.merge_range('A2:F2', 'Summary', merge_format)
    headings = ['PASS', 'Exception', 'CRASH', 'ANR', 'OOM', 'FAIL']
    worksheet.write_row('A3:F3', headings, bold)
    for i in range(0, len(headings)):
        worksheet.write_column('{}4'.format(chr(65+i)), str(test_results['{}'.format(headings[i])]), data_format)

    worksheet.merge_range('A6:F6', 'Statistics', merge_format)
    length = len(test_details['Status'])
    for i in range(0, length+1):
        worksheet.merge_range('C{0}:E{0}'.format(7+i), '', merge_format)
    headings1 = ['Round', 'Status', 'Error Message', 'comment']
    worksheet.write_row('A7:E7', headings1, bold)
    worksheet.write(6, 5, headings1[-1], data_format)
    worksheet.write_column('A8', range(1, length+1), data_format)
    worksheet.write_column('B8', test_details['Status'], data_format)
    worksheet.write_column('C8', test_details['Error Message'], data_format)
    worksheet.write_column('F8', ['' for i in range(1, length+1)], data_format)

def createPhoneSummary(workbook, sheet_name):
    # Summary of phone info for the performance reference.
    worksheet = workbook.add_worksheet(sheet_name)
    merge_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': '#cccccc',
    })
    bold = workbook.add_format({'bold': 1, 'border': 1})
    data_format = workbook.add_format({'border': 1})
    worksheet.merge_range('A1:G1', sheet_name+config['U_PROJECT_START_TIME'], merge_format)
    headings = [u'手机系统', u'手机名', u'手机品牌', u'手机内存', u'手机CPU内核数', u'虚拟机最大内存', u'APP最大内存']
    worksheet.set_column(0, 6, 15)
    worksheet.write_row('A2:G2', headings, bold)
    phone_info = [config['G_APP_DEVICE_VERSION'], 
                config['G_APP_DEVICE_MODEL'], 
                config['G_APP_DEVICE_BRAND'],
                config['G_APP_DEVICE_MEMORY'],
                config['G_APP_DEVICE_CPU_KERNELS'],
                config['G_APP_DEVICE_HEAPSIZE'],
                config['G_APP_DEVICE_HEAPGROWTHLIMIT']]
    worksheet.write_row('A3:G3', phone_info, data_format)

def createLineChart(workbook, sheet_name, results):
    items = len(results)
    length = len(results[-1])
    # create sheet
    worksheet = workbook.add_worksheet(sheet_name)
    # write title
    merge_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#cccccc',
    })
    worksheet.merge_range('A1:{}1'.format(chr(81 + items)), sheet_name + ' ' + config['U_PROJECT_START_TIME'], merge_format)
    # write headings
    if sheet_name == 'CPU':
        headings = ['duration', sheet_name]
    elif sheet_name == 'Memory':
        headings = ['duration', 'VSS', 'RSS']
    elif sheet_name == 'MemoryDetail':
        headings = ['duration', 'TOTAL Pss', 'Native Pss', 'Native Heap Size', 'Native Heap Alloc', 'Dalvik Pss', 'Dalvik Heap Size', 'Dalvik Heap Alloc']
    elif sheet_name == 'Activities':
        headings = ['duration', 'Activities']
    elif sheet_name == 'Flow':
        headings = ['duration', 'tcp_snd', 'tcp_rcv']
    elif sheet_name == 'FPS':
        headings = ['duration', 'FPS']
    bold = workbook.add_format({'bold': 1})
    worksheet.write_row('A2', headings, bold)
    # write data
    data_format = workbook.add_format({'border': 1})
    for i in range(items):
        worksheet.write_column('{}3'.format(chr(65+i)), results[i], data_format)
    # create line chart
    chart = workbook.add_chart({'type': 'line'})
    chart.set_size({'width': 1000, 'height': 450})
    for i in range(items-1):
        chart.add_series(
            {
                # each item define the line chr(66+i) ->(B-G)
                'name': '={0}!${1}$2'.format(sheet_name, chr(66+i)),
                'categories': '={0}!$A$3:$A${1}'.format(sheet_name, length + 1),
                'values': '={0}!${1}$3:${1}${2}'.format(sheet_name, chr(66+i), length + 1),
                'overlap': 10,
                'line': {
                    'width': 1.25,
                    'dash_type': 'solid',
                }
            })

    chart.set_title({'name': '{0} Tendency'.format(sheet_name)})
    if sheet_name == 'CPU' or sheet_name == 'Memory':
        chart.set_x_axis({'name': 'duration ({}s)'.format(os.getenv('U_LOG_DURATION'))})
    else:
        chart.set_x_axis({'name': 'duration (s)'})
    if sheet_name == 'CPU':
        chart.set_y_axis({'name': 'capacity (%)'})
    elif sheet_name == 'Activities':
        chart.set_y_axis({'name': 'count(n)'})
    elif sheet_name == 'FPS':
        chart.set_y_axis({'name': 'frame rate(fps)'})
    else:
        chart.set_y_axis({'name': 'capacity (K)'})

    # Set an Excel chart style. Colors with white outline and shadow.
    chart.set_style(10)
    # Insert the chart into the worksheet (with an offset).
    worksheet.insert_chart('{}3'.format(chr(66+items)), chart)

def report_format(workbook):
    merge_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'left',
        'valign': 'vcenter',
        'fg_color': '#cccccc',
    })
    bold_format = workbook.add_format({'bold': 1, 'border': 1})
    data_format = workbook.add_format({'border': 1})
    return merge_format, bold_format, data_format

