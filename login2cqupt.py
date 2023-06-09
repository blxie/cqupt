#  create by ourongxing
#  detail url: https://github.com/ourongxing/login4cqupt
import time
import requests
import argparse
import socket
import subprocess


def login(ip, args):
    args.ip = ip
    args.device = 0 if args.device == "pc" else 1
    res = requests.get(
        "http://192.168.200.2:801/eportal/?c=Portal&a=login&callback=dr1003&login_method=1&user_account=%2C{device}%2C{account}%40{operator}&user_password={password}&wlan_user_ip={ip}&wlan_user_ipv6=&wlan_user_mac=000000000000&wlan_ac_ip=&wlan_ac_name=".format_map(
            vars(args)
        )
    )
    if '"msg":""' in res.text:
        print("当前设备已登录")
        return
    elif r"\u8ba4\u8bc1\u6210\u529f" in res.text:
        # Unicode: 认证成功
        print("登录成功")
        return
    elif "bGRhcCBhdXRoIGVycm9y" in res.text:
        # 这是一个base64编码后的字符串，解码后得到的是：ldap auth error
        # 身份验证相关
        print("密码错误")
        return
    elif "aW51c2UsIGxvZ2luIGFnYWluL" in res.text:
        # 这是一个base64编码后的字符串，解码后得到的是：inuse, login again
        login(ip, args)
    else:
        print("您可能欠费停机")
        return


def get_ip():
    HOST = "8.8.8.8"  # 填写您要连接的主机名或IP地址
    PORT = 80  # 填写您要连接的端口号

    try:
        # 创建套接字连接
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"已连接到主机 {HOST} 的端口 {PORT}")
            ip = s.getsockname()[0]
            return ip
    except Exception as e:
        # 处理连接错误
        print(f"连接错误: {e}")


def get_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--account", default="3116431")
    parser.add_argument("--password", default="yjshl4_Z")
    parser.add_argument(
        "-o",
        "--operator",
        # default='xyw',  # 教师账号
        default="cmcc",
        choices=["cmcc", "telecom", "xyw"],
        help="operator, cmcc, telecom or teacher",
    )
    parser.add_argument("-d", "--device", default="pc", choices=["pc", "phone"], help="fake device, phone or pc")
    return parser.parse_args()


def is_connected():
    """
    使用Python的socket模块检测电脑宽带是否连接且可以正常使用
    """
    try:
        # connect to the host -- tells us if the host is actually reachable
        socket.create_connection(("8.8.8.8", 80))
        return True
    except OSError:
        pass
    return False


def connect_wifi():
    """连接指定名称的 WiFi"""
    # 替换ssid和password为你的WiFi网络名称和密码
    ssids = ["CQUPT-5G", "CQUPT-2.4G", "CQUPT"]

    # 循环尝试连接以CQUPT开头的网络，优先尝试CQUPT-5G
    for ssid in ssids:
        connect_wifi_command = f'netsh wlan connect name="{ssid}" ssid="{ssid}"'
        try:
            connect_wifi_process = subprocess.Popen(
                connect_wifi_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            time.sleep(1)  # 等待连接尝试完成，可以适当调整等待时间
            connect_wifi_process.terminate()  # 终止连接尝试进程
        except Exception as e:
            print(f"连接WiFi失败：{ssid}，错误信息：{e}")
            continue

        # 检查是否成功连接
        if check_wifi_connection(ssid):
            return True

    return False


def check_wifi_connection(ssid):
    """检查是否成功连接指定名称的 WiFi"""
    check_wifi_connection_command = "netsh wlan show interfaces"
    check_wifi_connection_process = subprocess.Popen(
        check_wifi_connection_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = check_wifi_connection_process.communicate()
    if output:
        output = output.decode("gbk")
        if ssid in output and "状态                 : 已连接" in output:
            return True

    return False


def run():
    try:
        if is_connected() or connect_wifi() == 0:
            print("WiFi or Ethernet connected, logining...")
            ip = get_ip()
            args = get_args()
            login(ip, args)
        else:
            print("No available network now, try again later!")
    except Exception as e:
        print(f"An error occurred: {str(e)}. Retrying in few seconds...")
        time.sleep(1)


if __name__ == "__main__":
    while True:
        run()
        time.sleep(60)
