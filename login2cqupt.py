import os
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

import logging
from logging.handlers import RotatingFileHandler


# 可不改
def get_ip():
    try:
        # 创建一个套接字并连接到外部主机
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # 使用Google的DNS服务器作为外部主机
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except socket.error as e:
        logger.error(f"Error @get_ip()\n{e}")
        return None


# TODO: pywifi
def extract_link_speed(link_speed):
    # 输入验证
    pattern = r"^(\d+(\.\d+)?)\s+(bps|Kbps|Mbps|Gbps)$"
    match = re.match(pattern, link_speed)
    if not match:
        raise ValueError("Invalid link speed format")

    # 单位转换映射
    conversion_factors = {"bps": 1, "Kbps": 1000, "Mbps": 1000000, "Gbps": 1000000000}

    speed = float(match.group(1))
    unit = match.group(3)

    # 单位转换
    try:
        if unit in conversion_factors:
            return speed * conversion_factors[unit]
        else:
            raise ValueError("Unsupported unit: " + unit)
    except ValueError as e:
        logger.error(f"Error @extract_link_speed()\n{e}")
        return 0


# TODO: pywifi
def get_net_adapter_info():
    command = "Get-NetAdapter -Name '以太网','WLAN*' | Select-Object Name, Status, MacAddress, LinkSpeed | ConvertTo-Json"
    try:
        output = subprocess.check_output(
            ["pwsh", "-Command", command], universal_newlines=True
        )
        adapter_info = json.loads(output)
        return adapter_info
    except subprocess.CalledProcessError as e:
        logger.error(f"Error @get_net_adapter_info()\n{e}")
        return None


# TODO: pywifi
def enable_adapter(adapter_name):
    command = f"Enable-NetAdapter -Name '{adapter_name}'"
    try:
        subprocess.check_output(["pwsh", "-Command", command], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error @enable_adapter()\n{e}")
        pass


# TODO: pywifi
def disable_adapter(adapter_name):
    command = f"Disable-NetAdapter -Name '{adapter_name}' -Confirm:$false"
    try:
        subprocess.check_output(["pwsh", "-Command", command], universal_newlines=True)
        logger.info(f"Successfully disabled NetAdapter: {adapter_name}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error @disable_adapter()\n{e}")
        pass


# TODO: pywifi
def enable_adapter_auto_connect(adapter_name):
    command = f"""
    $adapterName = "{adapter_name}"
    Get-NetAdapter -Name $adapterName | Set-NetIPInterface -Dhcp Enabled
    """
    subprocess.run(["pwsh", "-Command", command], capture_output=True, text=True)


# TODO: pywifi
def check_wifi_connection(adapter_name, wifi_name):
    try:
        # 执行 pwsh 命令获取 WLAN 连接的名称
        command = [
            "pwsh",
            "-Command",
            '(Get-NetConnectionProfile -InterfaceAlias "{}").Name'.format(adapter_name),
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            connection_name = result.stdout.strip()
            return wifi_name == connection_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Error @check_wifi_connection()\n{e}")

    return False


# TODO: pywifi
def scan_wifi(adapter_name, wifi_name):
    # 构造 netsh 命令
    command = [
        "pwsh",
        "-Command",
        f"netsh wlan show networks mode=Bssid '{adapter_name}'",
        "|",
        f"Select-String -Pattern {wifi_name}",  # 匹配所有包含 CQUPT 的字符串
    ]

    # 运行命令并获取输出结果
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        output = result.stdout.strip().split("\n")
        output = [re.sub(r"\x1b\[\d+m", "", line) for line in output]
        return output
    else:
        logger.error(f"Error @scan_wifi()\n{e}")
        return []


# TODO: pywifi
def connect_to_wifi(ssid, wlan_name):
    command = f'netsh wlan connect name="{ssid}" interface="{wlan_name}"'
    try:
        subprocess.check_output(["pwsh", "-Command", command], universal_newlines=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error @connect_to_wifi()\n{e}")
        return False


# 可不改
def browser_login(user_id="3116431", password="yjshl4_Z", network_type="移动"):
    logger.info(">> @browser_login()")

    # 初始化浏览器
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")  # 不打开窗口
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-redirects")
    driver = webdriver.Edge(options=options)
    driver.get("http://192.168.200.2")  # 进入登录页面

    xpath_success_msg = (
        '//*[@id="edit_body"]/div[2]/div[2]/form/div[@class="edit_lobo_cell"]'
    )
    xpath_username = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[3][@name="DDDDD"]'
    xpath_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[4][@name="upass"]'
    xpath_telecom = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[2]/input[@type="radio" and @value="@telecom"]'
    xpath_cmcc = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[3]/input[@type="radio" and @value="@cmcc"]'
    xpath_unicom = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[4]/input[@type="radio" and @value="@unicom"]'
    xpath_save_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[7][@type="checkbox" and @name="savePassword"]'
    xpath_login_button = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[2][@type="submit" and @value="登录"]'

    try:
        wait = WebDriverWait(driver, 10)
        success_message = wait.until(
            EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "您已经成功登录。")
        )
        if success_message:
            logger.info("手动登录成功")
            driver.quit()  # 关闭浏览器
            return True
    except Exception as e:
        logger.error(f"Error @browser_login()\n{e}")

    try:
        driver.find_element(By.XPATH, xpath_username).clear().send_keys(user_id)
        driver.find_element(By.XPATH, xpath_password).clear().send_keys(password)

        if network_type == "电信":
            target = driver.find_element(By.XPATH, xpath_telecom)
        elif network_type == "移动":
            target = driver.find_element(By.XPATH, xpath_cmcc)
        elif network_type == "联通":
            target = driver.find_element(By.XPATH, xpath_unicom)

        target.click()

        save_password_checkbox = driver.find_element(By.XPATH, xpath_save_password)
        save_password_checkbox.click()

        login_button = driver.find_element(By.XPATH, xpath_login_button)
        login_button.click()

        wait = WebDriverWait(driver, 3)
        status = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
        if status:
            logger.info("手动登录成功！")
        else:
            status = False

        driver.close()  # 关闭当前浏览器窗口
        return status
    except Exception as e:
        logger.error(f"Error @browser_login()\n{e}")
        return False


# 可不改
def terminal_login(login_msg):
    logger.info(">> @terminal_login()")
    url = "http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=,{device},{account}@{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac={mac}&wlan_ac_ip=&wlan_ac_name="

    try:
        res = requests.get(url.format_map(login_msg))
        # logger.info(url.format_map(login_msg))
        if '"msg":""' in res.text:
            logger.info(">> 当前设备已登录")
            return True
        elif r"\u8ba4\u8bc1\u6210\u529f" in res.text:
            # Unicode: 认证成功
            logger.info(">> 认证成功")
            return True
        elif "bGRhcCBhdXRoIGVycm9y" in res.text:
            # base64编码后的字符串：ldap auth error
            logger.info(">> 密码错误")
            return False
        elif "aW51c2UsIGxvZ2luIGFnYWluL" in res.text:
            # base64编码后的字符串：inuse, login again
            return terminal_login(login_msg)
        else:
            logger.info(">> 您可能欠费停机")
            return browser_login(
                user_id=login_msg["account"],
                password=login_msg["password"],
                network_type="移动",
            )
    except Exception as e:
        logger.error(f"Error @terminal_login()\n{e}")
        return False


def generate_random_mac():
    mac = [random.randint(0x00, 0xFF) for _ in range(6)]  # 生成6个0-255之间的随机整数
    mac_address = "".join(["{:02x}".format(x) for x in mac])  # 格式化为不带分隔符的MAC地址字符串
    return mac_address


# 可不改
def main(login_msg, logger):
    # 使用global关键字声明为全局变量
    global retry_times, MAX_RETRY_TIMES

    adapter_info = get_net_adapter_info()
    ssids = ["CQUPT-5G", "CQUPT", "CQUPT-2.4G"]
    login_msg["ip"] = get_ip()
    login_msg["mac"] = "000000000000"

    # logger.info(adapter_info)
    for adapter in adapter_info:
        enable_adapter(adapter["Name"])
    adapter_info = sorted(
        adapter_info, key=lambda x: extract_link_speed(x["LinkSpeed"]), reverse=True
    )

    for adapter in adapter_info:
        adapter_name = adapter["Name"]
        adapter_status = adapter["Status"]
        login_msg["mac"] = adapter["MacAddress"].replace("-", "").replace(":", "")
        # login_msg['mac'] = generate_random_mac()

        if "以太网" == adapter_name and "Up" == adapter_status:
            # 默认以太网自动连接网络
            logger.info("*" * 16 + " @Enthernet " + "*" * 16)

            time.sleep(3)
            if terminal_login(login_msg):
                logger.info(f">> {adapter_name} ✅\n")
                retry_times = 0
                break
            else:
                logger.info(f">> {adapter_name} ❌ {retry_times}\n")
                retry_times += 1
                return
        elif "WLAN" in adapter_name:
            logger.info("*" * 16 + " @WLAN " + "*" * 16)
            # WLAN 需要手动连接指定网络
            output = scan_wifi(adapter_name=adapter_name, wifi_name="CQUPT")
            if output:
                ssids = [item.split(": ", 1)[1] for item in output]
                ssids = sorted(
                    ssids,
                    key=lambda x: ("CQUPT-5G", "CQUPT-2.4G", "CQUPT").index(x)
                    if x in ("CQUPT-5G", "CQUPT-2.4G", "CQUPT")
                    else float("inf"),
                )
                for ssid in ssids:
                    logger.info(f">> {adapter_name}@{ssid} connect and login...")
                    if check_wifi_connection(adapter_name=adapter_name, wifi_name=ssid):
                        logger.info(f"{adapter_name} have connected {ssid}.")
                    elif connect_to_wifi(ssid=ssid, wlan_name=adapter_name):
                        logger.info(f"{adapter_name} ✅ {ssid}")
                    else:
                        logger.info(f"{adapter_name} ❌ {ssid}")
                        continue

                    if terminal_login(login_msg):
                        logger.info(f"{adapter_name}@{ssid} ✅\n")
                        retry_times = 0
                        return
                    else:
                        logger.info(f"{adapter_name}@{ssid} ❌ {retry_times}\n")
                        retry_times += 1
                        return

        if retry_times > MAX_RETRY_TIMES:
            disable_adapter(adapter_name)
            retry_times = 0


# 可不改
if __name__ == "__main__":
    log_dir = "D:/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(os.path.abspath(log_dir), "cqupt.log")
    log_max_size = 1024 * 128  # 最大日志文件大小（字节数）
    log_backup_count = 1  # 保留的备份文件数量

    handler = RotatingFileHandler(
        log_file, maxBytes=log_max_size, backupCount=log_backup_count, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 必须放在这里！即 logger.addHandler() 之前！
    logger.addHandler(handler)

    login_msg = dict(
        account="3116431", password="yjshl4_Z", operator="cmcc", device="pc"
    )
    login_msg["device"] = 0 if login_msg["device"] == "pc" else 1

    retry_times = 0
    MAX_RETRY_TIMES = 3

    while True:
        try:
            main(login_msg, logger)
            time.sleep(3)
        except Exception as e:
            logger.error(f"Error @__main__\n{e}")
