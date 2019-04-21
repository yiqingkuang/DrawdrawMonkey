# encoding=utf-8

import time
import datetime
import random
import threading
import unittest
from conf.config import config
from conf.setCondition import pre_condition, except_condition, post_condition, app
from core.util import create_log_path, combineTestResult


class AutoMonkey(unittest.TestCase):

    def setUp(self):
        # 创建log目录
        create_log_path()
        # 配置初始化参数，启动服务及记录日志等
        pre_condition()

    def test_monkey(self):
        # 生成一个线程，实时记录内存、流量和流畅度等信息
        app.start()
        time.sleep(2)
        # monkey 测试
        package = config['G_APP_PACKAGE_NAME']
        for i in range(1, 2):
            # 记录 logcat 日志
            app.record_android_log(str(i) + config['U_LOGCAT_LOG'])
            try:
                print ('Round: {}'.format(i))
                seed = random.randint(100, 10000)
                count = random.randint(50, 100)
                monkey_log = str(i) + config['U_MONKEY_LOG']
                traces_log = str(i) + config['U_TRACES_LOG']
                # 执行 monkey 命令，并保存日志
                app.run_monkey(package, 'L2', seed, 500, count, monkey_log, 'customized')
                # 分析 monkey 测试日志，统计结果
                res = app.analyze_monkey_log(monkey_log)
                if res == 0:
                    config['TEST_RESULTS']['PASS'] += 1
                elif res == -1:
                    config['TEST_RESULTS']['ANR'] += 1
                    # 导出 trace.txt 日志
                    app.get_error_log(traces_log)
                elif res == -2:
                    config['TEST_RESULTS']['Exception'] += 1
                elif res == -3:
                    config['TEST_RESULTS']['CRASH'] += 1
                elif res == -4:
                    config['TEST_RESULTS']['OOM'] += 1
                elif res == -5:
                    config['TEST_RESULTS']['FAIL'] += 1
                # 结束 logcat 进程
                app.stop_running_process('logcat')
                # 结束 APP 进程
                app.stop_running_app(config['G_APP_PACKAGE_NAME'])
            except Exception as error:
                # 异常处理
                print (str(error))
                except_condition(str(i))
        print ('Test Results: ', config['TEST_RESULTS'])
        # 结束线程
        app.stop()

    def tearDown(self):
        # 生成测试报告，绘制手机资源使用趋势图
        combineTestResult(config['TEST_RESULTS'], config['TEST_DETAILS'])
        # 结束服务
        post_condition()

if __name__ == '__main__':
    unittest.main()
