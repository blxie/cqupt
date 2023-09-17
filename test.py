import subprocess
import time
import requests
import socket

from logger import LogManager


def get_local_ip():
    try:
        # 创建一个套接字并连接到外部主机
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # 使用Google的DNS服务器作为外部主机
        local_ip = sock.getsockname()[0]
    except Exception as e:
        local_ip = None
    finally:
        sock.close()

    return local_ip


def login():
    ipaddr = get_local_ip()
    if not ipaddr:
        logger.error(
            "Get local ip address failed! Please check your network adapter status!\n"
        )
        return -1

    url = "http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1"
    data = {
        "user_account": ",0,3116431@cmcc",
        "user_password": "yjshl4_Z",
        "wlan_user_ip": f"{ipaddr}",
        # 等等其他直接从调试模式复制的请求数据
        # "wlan_user_mac": "000000000000",
    }
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
            logger.info("Accessed")
            return True
        else:
            logger.warning("Network is not available")
            return False
    except Exception as e:
        logger.error(f"@network_smooth: {e}")
        return False


def network_smooth():
    url = "https://www.baidu.com"
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        logger.info("Accessed")
        return True
    except requests.ConnectionError:
        logger.error("Network is not available")
        return False


def main():
    while True:
        if network_smooth():
            logger.info(f"Accessed")
        else:
            logger.info("#" * 16 + " New Conn... " + "#" * 16)
            logger.info(f"Login...")
            if login() == -1:
                break
        # time.sleep(60 * 30)  # 每半个小时检查一次
        time.sleep(2)


if __name__ == "__main__":
    logger = LogManager(log_path="./cqupt.log").initialize()
    main()
