import argparse
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


from logger import LogManager


# def browser_login(user_id="3116431", password="yjshl4_Z", network_type="移动"):
#     print(">> @browser_login()")

#     options = webdriver.EdgeOptions()
#     # options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-redirects")
#     options.add_argument("--disable-notifications")

#     driver = webdriver.Edge(options=options)
#     driver.get("http://192.168.200.2")

#     xpath_success_msg = '//*[@id="edit_body"]/div[2]/div[2]/form/div[@class="edit_lobo_cell"]'
#     xpath_username = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[3][@name="DDDDD"]'
#     xpath_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[4][@name="upass"]'
#     xpath_network_types = {
#         "电信": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[2]/input[@type="radio" and contains(@value,"@telecom")]',
#         "移动": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[3]/input[@type="radio" and contains(@value,"@cmcc")]',
#         "联通": '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/div[5]/span[4]/input[@type="radio" and contains(@value,"@unicom")]',
#     }
#     xpath_save_password = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[7][@type="checkbox" and contains(@name,"savePassword")]'
#     xpath_login_button = '//*[@id="edit_body"]/div[3]/div[1]/div/div[2]/div[1]/div/form/input[2][@type="submit" and contains(@value,"登录")]'

#     # wait = WebDriverWait(driver, 10)
#     # success_message = wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "您已经成功登录。"))
#     # if success_message:
#     #     print("手动登录成功")
#     #     driver.quit()
#     #     return True

#     username_input = driver.find_element(By.XPATH, xpath_username)
#     # print(username_input)
#     username_input.clear()
#     time.sleep(1)  # 等待1秒，确保文本已清空
#     username_input.send_keys(user_id)

#     username_input = driver.find_element(By.XPATH, xpath_password)
#     # print(username_input)
#     username_input.clear()
#     time.sleep(1)  # 等待1秒，确保文本已清空
#     username_input.send_keys(user_id)

#     # driver.find_element(By.XPATH, xpath_username).clear().send_keys(user_id)
#     # driver.find_element(By.XPATH, xpath_password).clear().send_keys(password)

#     # target = driver.find_element(By.XPATH, xpath_network_types.get(network_type, ""))
#     # target.click()

#     # save_password_checkbox = driver.find_element(By.XPATH, xpath_save_password)
#     # save_password_checkbox.click()

#     # login_button = driver.find_element(By.XPATH, xpath_login_button)
#     # login_button.click()

#     target = driver.find_element(By.XPATH, xpath_network_types.get(network_type, ""))
#     actions = ActionChains(driver)
#     actions.move_to_element(target).click().perform()

#     save_password_checkbox = driver.find_element(By.XPATH, xpath_save_password)
#     actions.move_to_element(save_password_checkbox).click().perform()

#     login_button = driver.find_element(By.XPATH, xpath_login_button)
#     actions.move_to_element(login_button).click().perform()

#     status_url = status_message = False
#     try:
#         wait = WebDriverWait(driver, 3)
#         try:
#             status_url = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
#         except TimeoutException:
#             status_message = wait.until(
#                 EC.text_to_be_present_in_element((By.XPATH, '//*[@id="message"][@class="edit_lobo_cell"]'), "AC认证失败")
#             )
#     except TimeoutException:
#         pass

#     print("登录成功！" if status_url or status_message else "登录失败")

#     # wait = WebDriverWait(driver, 3)
#     # status_url = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
#     # status_message = wait.until(EC.text_to_be_present_in_element((By.XPATH, xpath_success_msg), "AC认证失败"))

#     # if status_url or status_message:
#     #     print("登录成功！")
#     # else:
#     #     print("登录失败")

#     # wait = WebDriverWait(driver, 3)
#     # status = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
#     # if status:
#     #     print("手动登录成功！")
#     # else:
#     #     status = False

#     # driver.quit()
#     # return status


# browser_login()


def browser_login(user_id="3116431", password="yjshl4_Z", network_type="移动"):
    print(">> @browser_login()")

    options = webdriver.EdgeOptions()
    # options.add_argument("--headless")
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
    except TimeoutException:
        print("Error @browser_login()")
    finally:
        if status:
            print("手动登录成功")
            driver.quit()
            return True

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

    status = False
    try:
        wait = WebDriverWait(driver, 3)
        try:
            status = wait.until(EC.url_to_be("http://www.cqupt.edu.cn/"))
        except TimeoutException:
            status = wait.until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="message"][@class="edit_lobo_cell"]'), "AC认证失败")
            )
    except TimeoutException:
        pass
    print("登录成功！" if status else "登录失败")

    if status:
        print("手动登录成功！")
    else:
        status = False

    driver.quit()
    return status

browser_login()
