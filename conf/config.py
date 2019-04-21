# encoding=utf-8

import os
from datetime import datetime

config = dict()

# 项目开始时间
config['U_PROJECT_START_TIME'] = datetime.now().strftime('%Y%m%d_%H%M%S')
# 项目目录
config['U_PROJECT_DIR'] = os.getcwd()
# 日志目录
config['U_LOG_DIR'] = ''
# logcat 日志文件
config['U_LOGCAT_LOG'] = 'logcat.txt'
# top duration
config['U_LOG_DURATION'] = '5'
# top 日志文件
config['U_TOP_LOG_NAME'] = 'top.txt'
# meminfo 日志文件
config['U_MEMINFO_LOG_NAME'] = 'meminfo.txt'
# 流量 日志文件
config['U_FLOWIN_LOG_NAME'] = 'tcp_rcv.txt'
config['U_FLOWOUT_LOG_NAME'] = 'tcp_snd.txt'
# 流畅度 日志文件
config['U_GFXINFO_LOG_NAME'] = 'gfxinfo.txt'
# traces 日志文件
config['U_TRACES_LOG'] = 'traces.txt'
# monkey 日志文件
config['U_MONKEY_LOG'] = 'monkey_test.txt'
# monkey 包名
config['G_MONKEY_PACKAGE'] = 'com.android.commands.monkey'
# APP 包名
config['G_APP_PACKAGE_NAME'] = 'com.taobao.taobao'
# 测试结果
config['TEST_RESULTS'] = {'PASS': 0, 'ANR': 0, 'Exception': 0, 'CRASH': 0, 'OOM': 0, 'FAIL': 0}
config['TEST_DETAILS'] = {'Status': [], 'Error Message': []}
# CPU & Memory 信息
config['data'] = dict()

# 手机截屏目录
config['SDCARD_DIR'] = '/sdcard/'

# 手机信息:
# 手机 device name
config['G_APP_DEVICE_NAME'] = ''
# 手机系统版本
config['G_APP_DEVICE_VERSION'] = ''
# 手机名
config['G_APP_DEVICE_MODEL'] = ''
# 手机品牌
config['G_APP_DEVICE_BRAND'] = ''
# 手机内存
config['G_APP_DEVICE_MEMORY'] = ''
# 手机CPU数
config['G_APP_DEVICE_CPU_KERNELS'] = ''
# 单个虚拟机最大内存
config['G_APP_DEVICE_HEAPSIZE'] = ''
# 每个APP最大内存
config['G_APP_DEVICE_HEAPGROWTHLIMIT'] = ''
