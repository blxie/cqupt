import subprocess
import time
import requests
import socket

import yaml

from logger import LogManager


def get_local_ip():
    try:
        # 创建一个套接字并连接到外部主机
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # 使用Google的DNS服务器作为外部主机
        local_ip = sock.getsockname()[0]
    except Exception as e:
        local_ip = None
        logger.error(f"@get_local_ip(): {e} ❌")
    finally:
        sock.close()

    return local_ip


def login(config):
    ipaddr = get_local_ip()
    if not ipaddr:
        logger.error(
            "Get local ip address failed! Please check your network adapter status!\n"
        )
        return -1

    config["ip"] = ipaddr
    url = "http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1"
    templates = {
        "user_account": ",{device},{account}@{operator}",
        "user_password": "{password}",
        "wlan_user_ip": "{ip}",
        # "wlan_user_mac": "000000000000",
        # 等等其他直接从调试模式复制的请求数据,
    }
    data = {k: v.format_map(config) for k, v in templates.items()}
    response = requests.get(url, data)

    return response.status_code


def network_smooth():
    try:
        ret = subprocess.run(
            # "ping -c 1 www.baidu.com",
            "ping www.baidu.com",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        if ret.returncode == 0:
            return True
        else:
            logger.warning("Network is not available ❌")
            return False
    except Exception as e:
        logger.error(f"@network_smooth: {e}")
        return False


def network_smooth():
    # NOTE: only https, http not work!
    url = "https://www.baidu.com"
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        logger.error("Network is not available ❌")
        return False


def load_config(filename):
    try:
        with open(filename, "r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file '{filename}' not found.")
        return None


def main():
    while True:
        if network_smooth():
            logger.info(f"Accessed right ✅")
        else:
            logger.info("#" * 16 + " New Conn... " + "#" * 16)
            logger.info(f"Login...")
            if login(config) == -1:
                break

        sleep_time = config.get("sleep_time", 10)
        time.sleep(sleep_time)


def update_cfg(config: dict = None):
    devices = {"pc": 0, "phone": 1}
    operators = {
        "移动": "cmcc",
        "电信": "telecom",
        "联通": "unicom",
        "其他": "xyw",
    }

    config["device"] = devices.get(config["device"])
    config["operator"] = operators.get(config["operator"])


if __name__ == "__main__":
    config = load_config("config.yaml")
    update_cfg(config=config)

    log_path = config.get("log_path", "./cqupt.log")
    logger = LogManager(log_path=log_path).initialize()
    logger.info(f"updated config: {config} ✔️")

    main()
