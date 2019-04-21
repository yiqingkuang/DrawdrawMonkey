# encoding=utf-8

from conf.config import config
from core.appShell import AppShell


app = AppShell()

def pre_condition():
    global app
    # 设置 device name
    app.set_device_name()
    # 记录 top 日志
    app.adb_top()
    # 记录手机信息
    app.get_phone_info()
    app.get_total_mem()
    app.get_cpu_kernels()

def except_condition(traces_log):
    global app
    # 结束 logcat 进程
    app.stop_running_process('logcat')
    # 结束 monkey 进程
    app.stop_running_process(config['G_MONKEY_PACKAGE'])
    # 获取 ANR 日志
    app.get_error_log(traces_log + config['U_TRACES_LOG'])

def post_condition():
    global app
    # 结束 APP 进程
    app.stop_running_app(config['G_APP_PACKAGE_NAME'])
    # 结束 monkey 进程
    app.stop_running_process(config['G_MONKEY_PACKAGE'])
    # 结束 adb 进程
    app.kill_adb_process()

