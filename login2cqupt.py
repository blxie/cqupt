import argparse
import time
import socket
import subprocess
import requests
import re
import json
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from logger import LogManager


MAX_RETRY_TIMES = 3


class Login2CQUPT:
    def __init__(self, login_msg: dict = None):
        self.devices = {"pc": 0, "phone": 1}
        self.login_msg = dict(account="", password="", operator="移动", device="pc")
        self.operators = {
            "移动": "cmcc",
            "电信": "telecom",
            "联通": "unicom",
            "其他": "xyw",
        }

        self.update_attr(login_msg=login_msg)

    def update_attr(self, login_msg: dict = None):
        if login_msg:
            for key, value in login_msg.items():
                if key not in self.login_msg or self.login_msg[key] != value:
                    self.login_msg[key] = value

            self.login_msg["operator"] = self.operators.get(self.login_msg["operator"])
            self.login_msg["device"] = self.devices.get(self.login_msg["device"])

            self.logger = LogManager(login_msg["log_path"]).initialize()
            # self.logger.info(self.login_msg)
            self.logger.info(f"updated login_msg: {self.login_msg} ✔️")

    def get_local_ip(self):
        try:
            # 创建一个套接字并连接到外部主机
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))  # 使用Google的DNS服务器作为外部主机
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except socket.error as e:
            self.logger.error(f"Socket error @get_local_ip()\n{e}")
        except Exception as e:
            self.logger.error(f"Error @get_local_ip()\n{e}")
        return None

    def validate_link_speed(self, link_speed):
        pattern = r"^(\d+(\.\d+)?)\s+(bps|Kbps|Mbps|Gbps)$"
        match = re.match(pattern, link_speed)
        if not match:
            raise ValueError("Invalid link speed format")
        return match

    def extract_link_speed(self, link_speed):
        try:
            match = self.validate_link_speed(link_speed)

            conversion_factors = {"bps": 1, "Kbps": 1000, "Mbps": 1000000, "Gbps": 1000000000}

            speed = float(match.group(1))
            unit = match.group(3)

            if unit in conversion_factors:
                return speed * conversion_factors[unit]
            else:
                raise ValueError("Unsupported unit: " + unit)
        except ValueError as e:
            self.logger.error(f"ValueError @extract_link_speed(): {e}")
        except Exception as e:
            self.logger.error(f"Error @extract_link_speed(): {e}")

    def get_net_adapter_info(self):
        try:
            command = "Get-NetAdapter -Name '以太网','WLAN*' | Select-Object Name, Status, MacAddress, LinkSpeed | ConvertTo-Json"
            completed_process = subprocess.run(
                ["pwsh", "-Command", command], capture_output=True, text=True, encoding="gbk"
            )
            output = completed_process.stdout.strip()
            adapter_info = json.loads(output)
            if not isinstance(adapter_info, list):
                adapter_info = [adapter_info]
            # return json.dumps(adapter_info, ensure_ascii=False)
            return adapter_info
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error @get_net_adapter_info(): {e.returncode}\n{e.stderr}")
        except Exception as e:
            self.logger.error(f"Error @get_net_adapter_info()\n{e}")
        return None

    def enable_adapter(self, adapter_name):
        """
        pwsh 太消耗资源！
        """
        try:
            command = f"Enable-NetAdapter -Name '{adapter_name}'"
            result = subprocess.run(["pwsh", "-Command", command], capture_output=True, text=True, check=True)
            # result = subprocess.run(
            #     ["netsh", "interface", "set", "interface", adapter_name, "admin=enable"],
            #     capture_output=True,
            #     text=True,
            # )

            if result.returncode == 0:
                self.logger.info(f"Successfully enabled NetAdapter: {adapter_name}")
            else:
                self.logger.error(f"Failed to enable NetAdapter: {adapter_name}")
                self.logger.error(f"Command output: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @enable_adapter(): {e}")
            self.logger.error(f"Command output: {e.output}")
        except OSError as e:
            self.logger.error(f"OS error @enable_adapter(): {e}")
        except Exception as e:
            self.logger.error(f"Error @enable_adapter(): {e}")

    def disable_adapter(self, adapter_name):
        try:
            command = f"Disable-NetAdapter -Name '{adapter_name}' -Confirm:$false"
            result = subprocess.run(["pwsh", "-Command", command], capture_output=True, text=True)
            # result = subprocess.run(
            #     ["netsh", "interface", "set", "interface", adapter_name, "admin=disable"],
            #     capture_output=True,
            #     text=True,
            # )
            if result.returncode == 0:
                self.logger.info(f"Successfully disabled NetAdapter: {adapter_name}")
            else:
                self.logger.warning(f"Failed to disable NetAdapter: {adapter_name}")
                self.logger.warning(f"Command output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @disable_adapter(): {e}")
        except OSError as e:
            self.logger.error(f"OS error @disable_adapter(): {e}")
        except Exception as e:
            self.logger.error(f"Error @disable_adapter(): {e}")

    def enable_adapter_auto_connect(self, adapter_name):
        command = f"""
        $adapterName = "{adapter_name}"
        Get-NetAdapter -Name $adapterName | Set-NetIPInterface -Dhcp Enabled
        """
        try:
            result = subprocess.run(["pwsh", "-Command", command], capture_output=True, text=True)
            return result.stdout  # 返回命令执行的标准输出
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @enable_adapter_auto_connect(): {e}")
        except OSError as e:
            self.logger.error(f"OS error @enable_adapter_auto_connect(): {e}")
        except Exception as e:
            self.logger.error(f"Error @enable_adapter_auto_connect(): {e}")

    def check_wifi_connection(self, adapter_name, wifi_name):
        try:
            command = [
                "pwsh",
                "-Command",
                '(Get-NetConnectionProfile -InterfaceAlias "{}").Name'.format(adapter_name),
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                connection_name = result.stdout.strip()
                return wifi_name == connection_name
            else:
                self.logger.warning(f"Failed to execute PowerShell command @check_wifi_connection()")
                self.logger.warning(f"Return code: {result.returncode}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @check_wifi_connection(): {e}")
        except OSError as e:
            self.logger.error(f"OS error @check_wifi_connection(): {e}")
        except Exception as e:
            self.logger.error(f"Error @check_wifi_connection(): {e}")

        return False

    def scan_wifi(self, adapter_name, wifi_name):
        try:
            command = [
                "pwsh",
                "-Command",
                f"netsh wlan show networks mode=Bssid '{adapter_name}'",
                "|",
                f"Select-String -Pattern '{wifi_name}'",
            ]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                output = result.stdout.strip().split("\n")
                output = [re.sub(r"\x1b\[\d+m", "", line) for line in output]
                return output
            else:
                self.logger.error(f"Error executing scan_wifi():\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @scan_wifi(): {e}")
        except OSError as e:
            self.logger.error(f"OS error @scan_wifi(): {e}")
        except Exception as e:
            self.logger.error(f"Error @scan_wifi(): {e}")

        return []

    def connect_to_wifi(self, ssid, wlan_name):
        try:
            command = [
                "pwsh",
                "-Command",
                f'netsh wlan connect name="{ssid}" interface="{wlan_name}"',
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command execution error @connect_to_wifi(): {e}")
        except OSError as e:
            self.logger.error(f"OS error @connect_to_wifi(): {e}")
        except Exception as e:
            self.logger.error(f"Error @connect_to_wifi(): {e}")

        return False

    def browser_login(self, user_id="", password="", network_type="移动"):
        self.logger.info(">> @browser_login() v2!")

        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-redirects")

        driver = webdriver.Edge(options=options)
        driver.get("http://192.168.200.2")

        xpath_success_msg = '//*[@id="edit_body"]/div[2]/div[2]/form/div[@class="edit_lobo_cell"]'
        xpath_username = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[3][@name="DDDDD"]'
        xpath_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[4][@name="upass"]'
        xpath_network_types = {
            "电信": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[2]/input[@type="radio" and contains(@value,"@telecom")]',
            "移动": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[3]/input[@type="radio" and contains(@value,"@cmcc")]',
            "联通": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[4]/input[@type="radio" and contains(@value,"@unicom")]',
        }
        xpath_save_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[7][@type="checkbox" and contains(@name,"savePassword")]'
        xpath_login_button = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[2][@type="submit" and contains(@value,"登录")]'

        status = False
        try:
            wait = WebDriverWait(driver, 3)
            try:
                status = wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "您已经成功登录。"))
            except TimeoutException:
                xpath_success_msg = '//*[@id="message"][@class="edit_lobo_cell"]'
                status = wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "AC认证失败"))
        except TimeoutException as e:
            if status:
                self.logger.info("手动登录成功")
                driver.quit()
                return status

        """
        直接使用 clear() 会报错！要么不使用，要么先用变量接收，然后再clear()
        """
        # driver.find_element(By.XPATH, xpath_username).clear().send_keys(user_id)
        # driver.find_element(By.XPATH, xpath_password).clear().send_keys(password)
        driver.find_element(By.XPATH, xpath_username).send_keys(user_id)
        driver.find_element(By.XPATH, xpath_password).send_keys(password)

        """
        使用JavaScript执行点击操作，绕过元素被拦截的问题
        """
        network_type_radio = driver.find_element(By.XPATH, xpath_network_types.get(network_type, ""))
        driver.execute_script("arguments[0].click();", network_type_radio)
        # target.click()

        save_password_checkbox = driver.find_element(By.XPATH, xpath_save_password)
        driver.execute_script("arguments[0].click();", save_password_checkbox)
        # save_password_checkbox.click()

        login_button = driver.find_element(By.XPATH, xpath_login_button)
        driver.execute_script("arguments[0].click();", login_button)
        # login_button.click()

        try:
            wait = WebDriverWait(driver, 3)
            try:
                status = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
            except TimeoutException:
                xpath_success_msg = '//*[@id="message"][@class="edit_lobo_cell"]'
                status = wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "AC认证失败"))
        except TimeoutException as e:
            pass

        if status:
            self.logger.info("手动登录成功")
        else:
            status = False

        driver.quit()
        return status

    # 可不改
    def terminal_login(self):
        self.logger.info(">> @terminal_login()")
        url = "http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=,{device},{account}@{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac={mac}&wlan_ac_ip=&wlan_ac_name="

        try:
            res = requests.get(url.format_map(self.login_msg))
            # self.logger.info(url.format_map(self.login_msg))
            if re.search(r'"msg":""|认证成功', res.text):
                self.logger.info(">> 登录成功")
                return True
            elif "bGRhcCBhdXRoIGVycm9y" in res.text:
                # base64编码后的字符串：ldap auth error
                self.logger.info(">> 密码错误")
                return False
            elif "aW51c2UsIGxvZ2luIGFnYWluL" in res.text:
                # base64编码后的字符串：inuse, login again
                self.terminal_login()
            else:
                self.logger.info(">> 您可能欠费停机")
                return self.browser_login(
                    user_id=self.login_msg["account"],
                    password=self.login_msg["password"],
                    network_type="移动",
                )
        except requests.RequestException as e:
            self.logger.error(f"Error @terminal_login()\n{e}")
            return False
        except Exception as e:
            self.logger.error(f"Error @terminal_login()\n{e}")
            return False

    def generate_random_mac(self):
        mac = [random.randint(0x00, 0xFF) for _ in range(6)]  # 生成6个0-255之间的随机整数
        mac_address = "".join(["{:02x}".format(x) for x in mac])  # 格式化为不带分隔符的MAC地址字符串
        return mac_address

    def run(self):
        self.logger.info("#" * 16 + " New Conn. " + "#" * 16)

        global MAX_RETRY_TIMES
        self.login_msg["mac"] = "000000000000"
        self.login_msg["ip"] = self.get_local_ip()

        ssids = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]
        adapter_info = self.get_net_adapter_info()

        if not adapter_info:
            time.sleep(3)
            self.logger.warning("Not available netadapter! Retrying...\n")
            return

        for adapter in adapter_info:
            if adapter["Status"] not in ["Up", "Disconnected"]:
                self.enable_adapter(adapter["Name"])

        adapter_info = sorted(adapter_info, key=lambda x: self.extract_link_speed(x["LinkSpeed"]), reverse=True)

        for adapter in adapter_info:
            adapter_name = adapter["Name"]
            adapter_status = adapter["Status"]
            self.login_msg["mac"] = adapter["MacAddress"].replace("-", "").replace(":", "")
            # self.login_msg['mac'] = generate_random_mac()

            if MAX_RETRY_TIMES >= 3:
                self.disable_adapter(adapter_name)
                MAX_RETRY_TIMES = 0
                return

            if "以太网" == adapter_name and "Up" == adapter_status:
                # 默认以太网自动连接网络
                self.logger.info("*" * 12 + " @Enthernet " + "*" * 12)

                if self.terminal_login():
                    self.logger.info(f">> {adapter_name} ✅\n")
                    MAX_RETRY_TIMES = 0
                    return
                else:
                    self.logger.info(f">> {adapter_name} ❌ {MAX_RETRY_TIMES}\n")
                    MAX_RETRY_TIMES += 1
                    return
            elif "WLAN" in adapter_name:
                self.logger.info("*" * 12 + " @WLAN " + "*" * 12)

                try:
                    # WLAN 需要手动连接指定网络
                    output = self.scan_wifi(adapter_name=adapter_name, wifi_name="CQUPT")
                    ssids = [item.split(": ", 1)[1] for item in output]
                    ssids = sorted(
                        ssids,
                        key=lambda x: ("CQUPT-5G", "CQUPT-2.4G", "CQUPT").index(x)
                        if x in ("CQUPT-5G", "CQUPT-2.4G", "CQUPT")
                        else float("inf"),
                    )

                    for ssid in ssids:
                        self.logger.info(f">> {adapter_name}@{ssid} connect and login...")
                        if self.check_wifi_connection(adapter_name=adapter_name, wifi_name=ssid):
                            self.logger.info(f"{adapter_name} have connected {ssid}.")
                        elif self.connect_to_wifi(ssid=ssid, wlan_name=adapter_name):
                            self.logger.info(f"{adapter_name} ✔️ {ssid}")
                        else:
                            self.logger.info(f"{adapter_name} ❌ {ssid}")
                            MAX_RETRY_TIMES += 1
                            return

                        if self.terminal_login():
                            self.logger.info(f"{adapter_name}@{ssid} ✅\n")
                            MAX_RETRY_TIMES = 0
                            return
                        else:
                            self.logger.info(f"{adapter_name}@{ssid} ❌ {MAX_RETRY_TIMES}\n")
                            MAX_RETRY_TIMES += 1
                            return
                except Exception as e:
                    self.logger.error("@run(): output -- ssid: ", e)


def main():
    parser = argparse.ArgumentParser(description="Auto login script for CQUPT")
    parser.add_argument("-ac", "--account", default="3116431")
    parser.add_argument("-pwd", "--password", default="")
    parser.add_argument(
        "-opt",
        "--operator",
        default="移动",
        choices=["移动", "电信", "联通", "其他"],
        help="operator, cmcc, telecom, unicom or teacher",
    )

    parser.add_argument("--log_path", default="./cqupt.log", type=str, help="log path save dir")
    parser.add_argument("--sleep_time", default=3, type=int, help="interval time of auto login")
    parser.add_argument("-d", "--device", default="pc", choices=["pc", "phone"], help="fake device, phone or pc")

    args = parser.parse_args()
    app = Login2CQUPT(login_msg=vars(args))

    while True:
        try:
            app.run()
            time.sleep(args.sleep_time)
        except Exception as e:
            app.logger.error("!!!\n", e)


if __name__ == "__main__":
    main()
