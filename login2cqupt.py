import time
import re
import socket
import argparse
import subprocess
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By


class LoginIP:
    def __init__(self) -> None:
        self.ethernet_interface = "以太网"  # 以太网接口名称
        self.ssids = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]  # WiFi 列表
        self.login_msg = dict(account='3116431', password='yjshl4_Z', operator='cmcc', device='pc')

    def get_args(self):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--account', default='3116431')
        parser.add_argument('--password', default='yjshl4_Z')
        parser.add_argument(
            '-o',
            '--operator',
            # default='xyw',  # 教师账号
            default='cmcc',
            choices=['cmcc', 'telecom', 'xyw'],
            help='operator, cmcc, telecom or teacher')
        parser.add_argument('-d', '--device', default='pc', choices=['pc', 'phone'], help='fake device, phone or pc')
        return parser.parse_args()

    def update_args(self, args):
        for key, value in vars(args).items():
            if key not in self.login_msg or self.login_msg[key] != value:
                self.login_msg[key] = value
        self.login_msg['device'] = 0 if args.device == 'pc' else 1

    def browser_login(self, userID, password, network_type):
        # 初始化浏览器
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')  # 不打开窗口
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-redirects')
        driver = webdriver.Edge(options=options)
        driver.get("http://192.168.200.2")  # 进入登录页面

        xpath = ''
        msg = ''
        try:
            # 等待10秒钟，直到出现登录成功或失败的提示信息
            xpath = '//*[@id="edit_body"]/div[2]/div[2]/form/div[@class="edit_lobo_cell"]'
            # 使用等待条件来等待页面加载完成
            # wait = WebDriverWait(driver, 10)
            # success_message = wait.until(EC.presence_of_element_located((By.XPATH, "您已经成功登录。")))
            # print(success_message.text)  # 打印登录成功提示信息

            msg = driver.find_element(By.XPATH, xpath).text
            if msg == "您已经成功登录。":
                print("登录成功")
                driver.quit()  # 关闭浏览器
                return True
        except Exception as e:
            print(msg, e)  # 打印登录失败提示信息

        # 输入用户名和密码
        xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[3][@name="DDDDD"]'
        driver.find_element(By.XPATH, xpath).send_keys(userID)
        xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[4][@name="upass"]'
        driver.find_element(By.XPATH, xpath).send_keys(password)

        # 选择网络类型
        if network_type == "电信":
            xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[2]/input[@type="radio" and @value="@telecom"]'
        elif network_type == "移动":
            xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[3]/input[@type="radio" and @value="@cmcc"]'
        elif network_type == "联通":
            xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[4]/input[@type="radio" and @value="@unicom"]'

        target = driver.find_element(By.XPATH, xpath)
        driver.execute_script('arguments[0].click();', target)

        # 勾选保存密码
        xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[7][@type="checkbox" and @name="savePassword"]'
        target = driver.find_element(By.XPATH, xpath)
        driver.execute_script('arguments[0].click();', target)

        # 点击登录按钮
        xpath = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[2][@type="submit" and @value="登录"]'
        target = driver.find_element(By.XPATH, xpath)
        driver.execute_script('arguments[0].click();', target)

        time.sleep(3)
        status = False
        if driver.current_url == 'http://www.cqupt.edu.cn/':
            print("登录成功！")
            status = True

        # driver.get("http://192.168.200.2/")
        # time.sleep(3)

        driver.quit()  # 关闭浏览器
        return status

    def terminal_login(self):
        # url = 'http://192.168.200.2:801/eportal/?c=Portal&a=login&runback=dr1003&login_method=1&user_account=%2C{device}%2C{account}%40{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name='

        # url = 'http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=,0,3116431@cmcc&user_password=yjshl4_Z&wlan_user_ip=10.17.38.199&wlan_user_ipv6=&wlan_user_mac=0220b6ef3896&wlan_ac_ip=192.168.200.1&wlan_ac_name=NE40E-X16A&jsVersion=3.3.3&v=5360'

        url = 'http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=,{device},{account}@{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac={mac}&wlan_ac_ip=&wlan_ac_name='

        try:
            res = requests.get(url.format_map(self.login_msg))
            if '"msg":""' in res.text:
                print('>> 当前设备已登录')
                return True
            elif r'\u8ba4\u8bc1\u6210\u529f' in res.text:
                # Unicode: 认证成功
                print('>> 登录成功')
                return True
            elif 'bGRhcCBhdXRoIGVycm9y' in res.text:
                # 这是一个base64编码后的字符串，解码后得到的是：ldap auth error
                # 身份验证相关
                print(">> 密码错误")
                return False
            elif 'aW51c2UsIGxvZ2luIGFnYWluL' in res.text:
                # 这是一个base64编码后的字符串，解码后得到的是：inuse, login again
                self.terminal_login()
            else:
                print(">> 您可能欠费停机")
        except Exception as e:
            print("@terminal_login request 请求发生异常：", e)

        try:
            if self.browser_login(userID=self.login_msg['account'],
                                  password=self.login_msg['password'],
                                  network_type='移动'):
                return True
        except Exception as e:
            print(e)
            return False

    def interface_enabled(self, interface_name):
        cmd = f'netsh interface show interface "{interface_name}"'
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        if '已启用' in output:
            return True
        else:
            return False

    def interface_available(self, interface_name):
        cmd = f'netsh interface show interface "{interface_name}"'
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        if '已连接' in output:
            return True
        else:
            return False

    def get_interfaces_mac(self, interface_name):
        wlan_adapters = {}
        cmd_line = 'Get-NetAdapter | Where-Object { $_.Name -like "以太网" } | Select-Object -ExpandProperty MacAddress'
        try:
            # 执行 PowerShell 命令
            output = subprocess.check_output(['powershell', cmd_line], shell=True, encoding="gbk")

            # 解析输出结果
            output = output.strip()
            interface_mac = "".join(output.split('-'))
        except Exception as e:
            print(f"Error: {str(e)}")
        return interface_mac

    def surf(self):
        wlan_info = self.get_wlan_interfaces_name_and_mac()
        self.wlan_interfaces = wlan_info.keys()  # WLAN 接口名称列表
        self.login_msg['mac'] = self.get_interfaces_mac("以太网")

        if not self.interface_enabled(self.ethernet_interface):
            # 启用以太网接口
            subprocess.run(f'netsh interface set interface "{self.ethernet_interface}" admin=enable', shell=True)
            # 禁用所有已开启的 WLAN 接口
            for wlan_interface in self.wlan_interfaces:
                if self.interface_enabled(wlan_interface):
                    subprocess.run(f'netsh interface set interface "{wlan_interface}" admin=disable', shell=True)
        else:
            self.login_msg['ip'] = self.get_ip()
            print("—— Ethernet 已开启，连接登录...")
            if self.interface_available(self.ethernet_interface) and self.terminal_login():
                # 以太网可连接：禁用所有已开启的 WLAN 接口
                time.sleep(3)
                print("—— Ethernet 已连接！\n")
                for wlan_interface in self.wlan_interfaces:
                    if self.interface_enabled(wlan_interface):
                        subprocess.run(f'netsh interface set interface "{wlan_interface}" admin=disable', shell=True)
                        print(f">> @{wlan_interface} 已被禁用！")
            else:
                print(">> Ethernet 无法连接！启用 WLAN 连接 WiFi...")
                self.connect_wlan(wlan_info)

    def get_wlan_interfaces(self):
        output = subprocess.check_output('netsh interface show interface', shell=True)
        output = output.decode('gbk')

        lines = output.strip().split('\n')[2:]
        wlan_interfaces = []
        for line in lines:
            matches = re.findall(r'WLAN(?:\s\d+)?', line)
            if matches:
                interface_name = matches[0].strip()
                wlan_interfaces.append(interface_name)

        return wlan_interfaces

    def get_wlan_interfaces_name_and_mac(self):
        """使用正则表达式提取，但是运行效率影响较大！
        """
        # 运行 netsh wlan show interface 命令
        cmd_line = 'Get-NetAdapter | Where-Object { $_.Name -like "WLAN*" } | Select-Object Name, MacAddress'
        output = subprocess.check_output(['powershell', cmd_line], shell=True, encoding="gbk")

        # 根据换行符将输出拆分成行列表
        lines = output.split("\n")

        names = []
        mac_addrs = []

        # 查找包含"物理地址"的行
        for line in lines:
            import re
            # name = re.findall(r'WLAN(?:\s\d+)?|以太网', line)
            name = re.findall(r'WLAN(?:\s\d+)?', line)
            addr = re.findall(r'(?:[0-9A-Fa-f]{2}-){5}[0-9A-Fa-f]{2}', line)
            if name and addr:
                names.append(name[0].strip())
                mac_addrs.append("".join(addr[0].split('-')))

        return dict(zip(names, mac_addrs))

    def get_wlan_interfaces_name_and_mac(self):
        wlan_adapters = {}
        cmd_line = 'Get-NetAdapter | Where-Object { $_.Name -like "WLAN*" } | Select-Object Name, MacAddress'
        try:
            # 执行 PowerShell 命令
            output = subprocess.check_output(['powershell', cmd_line], shell=True, encoding="gbk")

            # 解析输出结果
            output = output.strip()
            if output:
                lines = output.splitlines()
                for line in lines[2:]:
                    parts = line.strip().split()
                    name = f'{parts[0]} {parts[1]}' if len(parts) == 3 else parts[0]
                    mac_address = parts[2] if len(parts) == 3 else parts[1]
                    wlan_adapters[name] = "".join(mac_address.split('-'))
        except Exception as e:
            print(f"Error: {str(e)}")
        return wlan_adapters

    def get_ip(self):
        try:
            # 创建一个套接字并连接到外部主机
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))  # 使用Google的DNS服务器作为外部主机
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except socket.error:
            return None

    def connect_wlan(self, wlan_info):
        # 以太网无法连接：按照 WLAN 接口列表的顺序依次启用并禁用其他 WLAN 接口
        for wlan_interface in self.wlan_interfaces:
            self.login_msg['mac'] = wlan_info[wlan_interface]

            if self.interface_available(wlan_interface) and self.terminal_login():
                print(f"\n—— 网络已通过 {wlan_interface} 连接登录！\n")
                return

            if not self.interface_enabled(wlan_interface):
                subprocess.run(f'netsh interface set interface "{wlan_interface}" admin=enable', shell=True)

            print(f"\n—— {wlan_interface} 已启用，连接 WiFi...")
            for ssid in self.ssids:
                try:
                    print(f"\n>> {wlan_interface}@{ssid} 连接登录...")
                    subprocess.run(f'netsh wlan connect name="{ssid}" ssid="{ssid}" interface="{wlan_interface}"',
                                   shell=True)
                    time.sleep(1)
                    if self.terminal_login():
                        time.sleep(1)
                        print(f">> 登录成功！\n")
                        return
                except Exception as e:
                    print(f">> 连接失败：{str(e)}")

    def main(self):
        try:
            args = self.get_args()
            self.update_args(args)

            self.surf()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    cqupt = LoginIP()

    while True:
        cqupt.main()
        time.sleep(1)
