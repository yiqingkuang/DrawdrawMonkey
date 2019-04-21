# -*- coding: utf-8 -*-

import os
import time
import threading
import re
from wsgiref.validate import validator
from conf.config import config


class AppShell(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False

    def __raise_error(self, msg=None):
        # Raise Exception with self-defined message.
        raise Exception(msg)

    def kill_adb_process(self):
        """
        Kill ADB Process.
        Examples:
        | Kill Adb Process |
        """
        try:
            status = os.system('taskkill /f /im adb.exe')
            if status == 0:
                print ('Pass! Killed ADB Process.')
            else:
                self.__raise_error('Fail! Could NOT kill ADB Process.')
        except Exception as e:
            print (str(e))

    def start_adb_service(self):
        """
        Start ADB Service.
        Examples:
        | Start Adb Service |
        """
        try:
            text = os.popen('adb start-server')
            content = text.read()
            print (content)
            if '5037' not in content:
                self.__raise_error('Error: start ADB server failed. %s' % content)
            else:
                print ('Pass! ADB server started.')
        except Exception as e:
            print (str(e))

    def get_device_name(self):
        """
        Get Devices Name through ADB command.
        Examples:
        | ${device_name} | Get Adb Devices |
        """
        device_name = ''
        adb_devices = "adb devices"
        try:
            text = os.popen(adb_devices)
            content = text.read().strip()
            print (content)
            res = content.splitlines()
            if 'device' not in content:
                self.__raise_error('Error: Could Not get device -> {}'.format(res[-1].split()[1]))
            device_name = res[-1].split()[0]
        except Exception as e:
            if str(e) == 'list index out of range':
                self.__raise_error('Error: Could NOT find device! Please check the phone has been attached to TestBed.')
            else:
                print (str(e))
        return device_name

    def set_device_name(self, name=None):
        """
        Set Devices Name after get its name through ADB command.
        Examples:
        | Set Device Name |
        """
        if name == None:
            device_name = self.get_device_name()
        else:
            device_name = name
        if config['G_APP_DEVICE_NAME'] != '' and config['G_APP_DEVICE_NAME'] == device_name:
            print ('-'*30)
            print ('Pass! Set device name!')
            print ('Device Name:' + config['G_APP_DEVICE_NAME'])
            print ('-'*30)
        elif device_name == '':
            self.__raise_error('FAIL: Could NOT get device name!')
        else:
            config['G_APP_DEVICE_NAME'] = str(device_name)
            print ('-'*30)
            print ('Pass! Set device name!')
            print ('Device Name: ' + config['G_APP_DEVICE_NAME'])
            print ('-'*30)

    def get_phone_info(self, dev=None):
        if dev is None:
            dev = config['G_APP_DEVICE_NAME']
        cmd = "adb -s {} shell cat /system/build.prop".format(dev)
        print (cmd)
        lines = os.popen(cmd).readlines()
        for line in lines:
            if 'version.release' in line:
                config['G_APP_DEVICE_VERSION'] = line.strip().split('=')[1]  # Android 系统
            elif 'ro.product.model' in line:
                config['G_APP_DEVICE_MODEL'] = line.strip().split('=')[1]  # 手机名
            elif 'ro.product.brand' in line:
                config['G_APP_DEVICE_BRAND'] = line.strip().split('=')[1]  # 手机品牌
            elif 'vm.heapsize' in line:
                config['G_APP_DEVICE_HEAPSIZE'] = line.strip().split('=')[1]  # 单个虚拟机最大内存
            elif 'vm.heapgrowthlimit' in line:
                config['G_APP_DEVICE_HEAPGROWTHLIMIT'] = line.strip().split('=')[1]  # 每个APP最大内存

    def get_total_mem(self, dev=None):
        # 获取手机内存
        if dev is None:
            dev = config['G_APP_DEVICE_NAME']
        try:
            cmd = 'adb -s {} shell cat /proc/meminfo'.format(dev)
            print (cmd)
            res = os.popen(cmd)
            for line in res.readlines():
                if 'MemTotal:' in line:
                    config['G_APP_DEVICE_MEMORY'] = line.split('MemTotal:')[1].strip()
                    break
        except Exception as e:
            print (str(e))

    def get_cpu_kernels(self, dev=None):
        # 获取手机CPU内核数
        if dev is None:
            dev = config['G_APP_DEVICE_NAME']
        try:
            cmd = 'adb -s {} shell cat /proc/cpuinfo |findstr processor'.format(dev)
            print (cmd)
            content = os.popen(cmd)
            res = content.readlines()
            if 'processor' in res[0]:
                config['G_APP_DEVICE_CPU_KERNELS'] = len(res)
            else:
                print ('Could NOT get CPU kenels!')
        except Exception as e:
            print (str(e))

    def adb_install_package(self, apk=None, package_name=None):
        """
        Install packages through ADB command.
        Examples:
        |     Adb Install Package    | ${apk_name} | ${package_name} |
        """
        if apk is None:
            apk = config['G_APP_PACKAGE_NAME']
        # else:
        # 	apk = os.path.join(config['G_APP_PACKAGE_NAME'], apk)

        if package_name is None:
            package_name = config['G_APP_PACKAGE_NAME']
        if self.is_package_installed(package_name):
            self.adb_uninstall_package(package_name)
        try:
            cmd = 'adb -s {} install -r {}'.format(config['G_APP_DEVICE_NAME'], apk)
            print (cmd)
            text = os.popen(cmd)
            content = text.read()
            print (content)
            if 'Success' in content:
                print ('Pass: Install {} succeeded. Version: {}'.format(package_name, apk))
            else:
                self.__raise_error('Fail: Could NOT install {}'.format(package_name))
        except Exception as e:
            print (str(e))

    def adb_uninstall_package(self, package_name=None):
        """
        Uninstall packages through ADB command.
        Examples:
        |    Adb Uninstall Package    | ${package_name} |
        """
        if package_name is None:
            package_name = config['G_APP_PACKAGE_NAME']
        if not self.is_package_installed(package_name):
            self.__raise_error('Fail: APP {} is not installed.'.format(package_name))
        try:
            cmd = 'adb -s {} uninstall {}'.format(config['G_APP_DEVICE_NAME'], package_name)
            print (cmd)
            text = os.popen(cmd)
            content = text.read()
            print (content)
            if 'Success' in content:
                print ('Pass: Uninstall {} succeeded.'.format(package_name))
            else:
                self.__raise_error('Fail: Could NOT uninstall {}'.format(package_name))
        except Exception as e:
            print (str(e))

    def is_package_installed(self, package_name):
        """
        Check target package is installed through ADB command.
        Examples:
        | ${status} | Is Package Installed |
        """
        packages = self.get_third_party_packages()
        if package_name in packages:
            return True
        else:
            return False

    def get_third_party_packages(self):
        """
        Get Third-party packages through ADB command.
        Examples:
        | ${apk_name} | Get Third Party Packages |
        """
        apks = []
        try:
            f = os.popen('adb shell pm list package -3')
            for x in f.readlines():
                apks.append(x.strip().split(':')[1])
            return apks
        except Exception as e:
            print (str(e))


    def record_android_log(self, filename, path=None):
        """
        Get Log from phone through ADB logcat.
        Default directory: current directory.
        Examples:
        | Record Android Log | filename | path=None |
        """

        if path is None:
            file = os.path.join(config['U_LOG_DIR'], filename) # Default File Path
        else:
            file = os.path.join(path, filename)

        try:
            # run command in background: start /b xxx
            cmd = 'start /b adb logcat -v time > {}'.format(file)
            print ('-'*80)
            print ('INFO: try to save logcat result.')
            print (cmd)
            status = os.system(cmd)
            if status == 0:
                print ('Pass! Logcat is running...')
            else:
                self.__raise_error('Fail! Could NOT start Logcat.')
            print ('-'*80)
        except Exception as e:
            print (str(e))

    def get_error_log(self, traces_log, path=None):
        """
        Pull Log from phone through ADB command.
        Default directory: current directory.
        Examples:
        | Get Error Log |
        """

        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], traces_log)
        else:
            filename = os.path.join(path, traces_log)

        try:
            # Get ANR log.
            cmd = 'adb pull /data/anr/traces.txt {}'.format(filename)
            print ('-'*80)
            print ('INFO: Get ANR log.')
            print (cmd)
            status = os.system(cmd)
            time.sleep(2)
            if status == 0 and os.path.exists(filename):
                print ('Pass! Saved ANR log.')
            else:
                self.__raise_error('Fail! Could NOT save Error log.')
            print ('-'*80)
        except Exception as e:
            print (str(e))

    def run_monkey(self, package, level, seed, throttle, count, log, pattern='normal', path=None):
        """
        Run Monkey to test targe packages through ADB command.
        Examples:
        | Run Monkey | package name | level | seed | throttle | count |
        | Run Monkey | package name | level1 | 1000 | 2000 | 15000 |
        | Run Monkey | package name | 0 | 1000 | 500 | 10000 | customized |
        """
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], log) # Default File Path
        else:
            filename = os.path.join(path, log)

        package = '-p {}'.format(package)

        if str(level) == 'level0' or str(level) == 'L0':
            level = '-v'
        elif str(level) == 'level1' or str(level) == 'L1':
            level = '-v -v'
        elif str(level) == 'level2' or str(level) == 'L2':
            level = '-v -v -v'
        else:
            self.__raise_error('Parameter Error!')

        seed = '-s {}'.format(seed)
        throttle = '--throttle {}'.format(throttle)
        if pattern.lower() == 'normal':
            cmd = 'adb shell monkey {} {} {} {} {} >{}'.format(package, level, seed, throttle, count, filename)
        elif pattern.lower() == 'customized':
            cmd = 'adb shell monkey {} {} --hprof --pct-touch 40 --pct-motion 25 --pct-majornav 10 --pct-rotation 10 --pct-appswitch 10 {} {} {} >{}'.format(package, level, seed, throttle, count, filename)
        else:
            print ('Error: Wrong Parameter.')
        print ('cmd: ')
        print (cmd)

        try:


            print( 'chenmin')

            status = os.system(cmd)
            if status == 0:
                print ('Pass! Monkey test finished.')
            elif status == 1:
                print ('fiald!')
            else:
                self.__raise_error('Fail! Could NOT run monkey test.')
        except Exception as e:
            print (str(e))

    def analyze_monkey_log(self, log_file, path=None):
        """
        Analyze monkey test result via log file.
        Examples:
        | ${status} | Analyze Monkey Log |
        """
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], log_file) # Default File Path
        else:
            filename = os.path.join(path, log_file)

        with open(filename, 'r') as fp:
            content = fp.read()
            if 'Monkey finished' in content:
                print ('INFO: Monkey test succeeded.')
                config['TEST_DETAILS']['Status'].append('PASS')
                config['TEST_DETAILS']['Error Message'].append('')
                return 0
            elif 'ANR in ' in content:
                print ('INFO: Monkey test causes ANR')
                config['TEST_DETAILS']['Status'].append('ANR')
                for line in content.splitlines():
                    if 'ANR in ' in line:
                        config['TEST_DETAILS']['Error Message'].append(line)
                return -1
            elif 'Exception' in content:
                print ('INFO: Monkey test crashed')
                config['TEST_DETAILS']['Status'].append('Exception')
                for line in content.splitlines():
                    if 'java' in line and 'Exception' in line:
                        config['TEST_DETAILS']['Error Message'].append(line)
                return -2
            elif 'CRASH' in content:
                print ('INFO: Monkey test crashed')
                config['TEST_DETAILS']['Status'].append('CRASH')
                for line in content.splitlines():
                    if 'Long Msg:' in line:
                        config['TEST_DETAILS']['Error Message'].append(line)
                return -3
            elif 'OOM' in content:
                print ('INFO: Monkey test OOM')
                config['TEST_DETAILS']['Status'].append('OOM')
                for line in content.splitlines():
                    if 'OOM' in line:
                        config['TEST_DETAILS']['Error Message'].append(line)
                return -4
            else:
                print ('INFO: Monkey test failed.')
                config['TEST_DETAILS']['Status'].append('FAIL')
                config['TEST_DETAILS']['Error Message'].append('')
                return -5

    def check_app_status(self, package):
        """
        Check target APP Status: running or stopped.
        Examples:
        | ${status} | Check APP Status | ${package} |
        """
        try:
            cmd = 'adb shell ps | findstr {}'.format(package)
            text = os.popen(cmd)
            content = text.read()
            if content == '':
                print ('Status: Target APP {} is stopped.'.format(package))
                return False
            elif package in content:
                print ('Status: Target APP {} is running.'.format(package))
                return True
            else:
                self.__raise_error("Error! Cound NOT get target APP {}'s status".format(package))
        except Exception as e:
            print (str(e))

    def stop_running_app(self, package):
        """
        Stop Running APP if it is running.
        Examples:
        | Stop Running APP | ${package} |
        """
        try:
            status = self.check_app_status(package)
            if status is True:
                cmd = 'adb shell am force-stop {}'.format(package)
                text = os.popen(cmd)
                content = text.read()
                if content == '':
                    print ('PASS! Target APP {} has stopped.'.format(package))
                else:
                    self.__raise_error("Fail! Cound NOT STOP target APP {}".format(package))
            elif status is False:
                print ('PASS! Target APP {} is already stopped.'.format(package))
            else:
                self.__raise_error("Error! Cound NOT STOP target APP {}".format(package))
        except Exception as e:
            print (str(e))

    def stop_running_process(self, package):
        """
        Stop Running Process if it is running via pid.
        Examples:
        | Stop Running Process | ${package} |
        """
        try:
            pid = self.get_app_pid(package)
            if pid != -1 and pid != -2:
                cmd = 'adb shell kill pid {}'.format(pid)
                status = os.system(cmd)
                if status == 0:
                    print ('PASS! Target APP {} has stopped.'.format(package))
                else:
                    self.__raise_error("Fail! Cound NOT STOP target Process {}".format(pid))
            else:
                self.__raise_error("Error! Cound NOT STOP target Process {}".format(pid))
        except Exception as e:
            print (str(e))

    def get_app_pid(self, package):
        """
        Check target APP Status: running or stopped.
        Examples:
        | ${pid} | Check APP Status | ${package} |
        """
        try:
            cmd = 'adb shell ps | findstr {}'.format(package)
            text = os.popen(cmd)
            content = text.read().strip()
            if package in content:
                pid = content.split()[1]
                print ('Status: Target APP {} is running: {}'.format(package, pid))
                return pid
            else:
                print ('Status: Target APP {} is stopped.'.format(package))
                return -1
        except Exception as e:
            print (str(e))
            return -2

    def get_app_uid(self, pid):
        uid_cmd = 'adb shell cat /proc/{}/status |findstr Uid'.format(pid)
        print (uid_cmd)
        try:
            if pid != -1:
                content = os.popen(uid_cmd)
                content = content.read().strip()
                if 'Uid:' in content:
                    uid = content.split()[1]
                    print ('Uid: {}'.format(uid))
                    return uid
                else:
                    print ('FAIL: Could not get UID!')
                    return -1
            else:
                return -1
        except Exception as e:
            print (str(e))


    def get_flow(self, uid):
        tcp_snd = os.path.join(config['U_LOG_DIR'], config['U_FLOWOUT_LOG_NAME'])
        tcp_rcv = os.path.join(config['U_LOG_DIR'], config['U_FLOWIN_LOG_NAME'])
        snd_cmd = 'adb shell cat /proc/uid_stat/{}/tcp_snd >>{}'.format(uid, tcp_snd)
        rcv_cmd = 'adb shell cat /proc/uid_stat/{}/tcp_rcv >>{}'.format(uid, tcp_rcv)
        print (snd_cmd)
        print (rcv_cmd)
        try:
            if uid != -1:
                os.popen('{} && {}'.format(snd_cmd, rcv_cmd))
        except Exception as e:
            print (str(e))

    def adb_top(self, duration=None, package=None, path=None):
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], config['U_TOP_LOG_NAME'])
        else:
            filename = os.path.join(path, config['U_TOP_LOG_NAME'])
        if duration is None:
            duration = config['U_LOG_DURATION']
        top_cmd = 'start /b adb shell top -m 10 -d {} >{}'.format(duration, filename)
        print (top_cmd)
        try:
            os.popen(top_cmd)
            print ('Pass! adb top is running...')
        except Exception as e:
            print (str(e))

    def getprop_heapsize(self, package=None):
        # get heap limit size
        filename = os.path.join(config['U_LOG_DIR'], config['U_MEMINFO_LOG_NAME'])
        if package is None:
            package = config['G_APP_PACKAGE_NAME']
        heap_info = 'adb shell getprop | findstr heap'
        print (heap_info)
        try:
            content = os.popen(heap_info)
            content = content.read()
            with open(filename, 'w') as fp:
                fp.write(content)
        except Exception as e:
            print (str(e))


    def get_gfxinfo(self, package=None, path=None):
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], config['U_GFXINFO_LOG_NAME'])
        else:
            filename = os.path.join(path, config['U_GFXINFO_LOG_NAME'])
        if package is None:
            package = config['G_APP_PACKAGE_NAME']
        _adb = "adb shell dumpsys gfxinfo {}".format(package)
        print (_adb)
        try:
            results = os.popen(_adb).read().strip()
            frames = [x for x in results.split('\n') if validator(x)]
            frame_count = len(frames)
            jank_count = 0
            vsync_overtime = 0
            render_time = 0
            for frame in frames:
                time_block = re.split(r'\s+', frame.strip())

                if len(time_block) == 4:
                    try:
                        render_time = float(time_block[0]) + float(time_block[2]) + float(time_block[3])
                    except Exception as e:
                        render_time = 0

                '''
                当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
                那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
                如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

                最后的计算方法思路：
                执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
                需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

                所以FPS的算法可以变为：
                m / （m + 额外的垂直同步脉冲） * 60
                '''
                if render_time > 16.67:
                    jank_count += 1
                    if render_time % 16.67 == 0:
                        vsync_overtime += int(render_time / 16.67) - 1
                    else:
                        vsync_overtime += int(render_time / 16.67)

            _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
            print ("-----fps------")
            print (_fps)
            with open(filename, 'a') as fp:
                fp.write(str(_fps) + '\n')
        except Exception as e:
            print (str(e))

    def meminfo(self, package=None, path=None):
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], config['U_MEMINFO_LOG_NAME'])
        else:
            filename = os.path.join(path, config['U_MEMINFO_LOG_NAME'])
        if package is None:
            package = config['G_APP_PACKAGE_NAME']
        meminfo = 'start /b adb shell dumpsys meminfo {} >>{}'.format(package, filename)
        try:
            os.popen(meminfo)
            print (meminfo)
        except Exception as e:
            print (str(e))

    def adb_screencap(self, image, path=None):
        image = os.path.join(config['SDCARD_DIR'], image)
        if path is None:
            filename = os.path.join(config['U_LOG_DIR'], image)
        else:
            filename = os.path.join(path, image)
        screenshot = 'adb shell screencap -p "{}"'.format(image)
        save_image = 'adb pull "{}" {}'.format(image, filename)
        rm_image = 'adb shell rm "{}"'.format(image)
        try:
            status = os.system(screenshot)
            if status == 0:
                print (screenshot)
            else:
                print ("Error: couldn't save screenshot.")
            os.system(save_image)
            os.system(rm_image)
        except Exception as e:
            print (str(e))

    def run(self):
        package = config['G_APP_PACKAGE_NAME']
        duration = float(config['U_LOG_DURATION'])
        while not self.thread_stop:
            pid = self.get_app_pid(package)
            if pid != -1 or pid != -2:
                # Record info when app is running.
                print ('Record info:')
                self.meminfo()
                self.get_gfxinfo()
                uid = self.get_app_uid(pid)
                self.get_flow(uid)
                time.sleep(duration)

    def stop(self):
        self.thread_stop = True
