from logging.handlers import RotatingFileHandler
import os
import sys
import logging
import winreg
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QCheckBox,
    QComboBox,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QDesktopWidget,
    QMessageBox,
    QDialog,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QFile, pyqtSlot, QTimer

from login2cqupt import Login2CQUPT


class LogManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        # log_dir = "D:/logs"
        log_dir = "."
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(os.path.abspath(log_dir), "app.log")
        log_max_size = 1024 * 128  # 最大日志文件大小（字节数）
        log_backup_count = 1  # 保留的备份文件数量

        handler = RotatingFileHandler(log_file, maxBytes=log_max_size, backupCount=log_backup_count, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # 必须放在这里！即 self.logger.addHandler() 之前！
        logger.addHandler(handler)

        return logger


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.initUI()

        ## 设置定时器
        self.timer = QTimer(self)  # 将定时器对象设为成员变量
        self.timer.timeout.connect(self.login)

    def initUI(self):
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_tray_icon()

    def create_widgets(self):
        self.username_label = QLabel("用户名:")
        self.password_label = QLabel("密码:")
        self.account_type_label = QLabel("账号类型:")

        self.username_input = QLineEdit()
        self.username_input.setText("3116431")  # 设置默认值
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("yjshl4_Z")  # 设置默认值

        self.login_button = QPushButton("登录")
        self.startup_checkbox = QCheckBox("开机自启动")

        self.account_type_combo_box = QComboBox()
        self.account_type_combo_box.addItem("移动")
        self.account_type_combo_box.addItem("联通")
        self.account_type_combo_box.addItem("电信")
        self.account_type_combo_box.addItem("其他")

        self.timer_checkbox = QCheckBox("定时登录")

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.account_type_label)
        layout.addWidget(self.account_type_combo_box)
        layout.addWidget(self.login_button)
        layout.addWidget(self.startup_checkbox)
        layout.addWidget(self.timer_checkbox)

        self.setLayout(layout)

    def create_connections(self):
        self.login_button.clicked.connect(self.login)
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        self.timer_checkbox.stateChanged.connect(self.toggle_timer_login)

    def closeEvent(self, event):
        self.hide()
        self.show_exit_dialog()
        event.ignore()

    def closeEvent(self, event):
        self.hide()
        self.tray_icon.show()  # 重要！！！
        # self.tray_icon.showMessage(
        #     "My Application", "程序已最小化到系统托盘", QSystemTrayIcon.Information, 1000  # 显示提示消息的持续时间（毫秒）
        # )
        print("程序已最小化到系统托盘")
        event.ignore()

    def show_exit_dialog(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("退出确认")
        msg_box.setText("是否将程序运行在后台？")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        msg_box.buttonClicked.connect(self.handle_exit_dialog)
        msg_box.show()

    def handle_exit_dialog(self, button):
        print(button.text())
        if button.text() == "&Yes":
            self.tray_icon.show()
            self.hide()
            # self.tray_icon.showMessage(
            #     "My Application", "程序已最小化到系统托盘", QSystemTrayIcon.Information, 1000  # 显示提示消息的持续时间（毫秒）
            # )
            print("程序已最小化到系统托盘")
        else:
            self.tray_icon.hide()
            self.close()

    def stop_login_timer(self):
        self.timer.stop()

    def start_login_timer(self):
        if self.timer_checkbox.isChecked():
            self.timer.start(30000)  # 设置定时器间隔为30秒
        else:
            self.stop_login_timer()

    @pyqtSlot(int)
    def toggle_timer_login(self, state):
        if state == Qt.Checked:
            self.start_login_timer()
            print("已启用定时登录")
        else:
            self.stop_login_timer()
            print("已禁用定时登录")

    @pyqtSlot(int)
    def toggle_startup(self, state):
        if state == Qt.Checked:
            self.add_startup_registry_key()
            print("已开启开机自启动")
        else:
            self.remove_startup_registry_key()
            print("已关闭开机自启动")

    def add_startup_registry_key(self):
        app_path = sys.argv[0]
        app_name = "My Application"

        # 添加注册表项
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)

    def remove_startup_registry_key(self):
        app_path = sys.argv[0]
        app_name = "My Application"

        # 删除注册表项
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, app_name)
            winreg.CloseKey(key)
        except WindowsError:
            pass

    def show_window(self):
        self.showNormal()
        self.activateWindow()
        self.tray_icon.hide()

    def close_application(self):
        self.tray_icon.hide()
        # self.close()
        QApplication.instance().quit()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        account_type = self.account_type_combo_box.currentText()

        # 在这里可以编写登录逻辑
        print(f"用户名: {username}")
        print(f"密码: {password}")
        print(f"账号类型: {account_type}")

        login_msg = dict(account=username, password=password, operator=account_type, device="pc")
        logapp.update_attr(login_msg=login_msg)
        logapp.run()

    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = "icons/icon.jpg"  # 替换为自己的图标路径
        file = QFile(icon_path)
        if file.exists():
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(QIcon.fromTheme("dialog-information"))  # 使用默认图标
            # logger.warning(f"图标文件不存在或路径错误: {icon_path}")
            print(f"图标文件不存在或路径错误: {icon_path}")
        self.tray_icon.setToolTip("My Application")

        tray_menu = QMenu()
        self.show_action = QAction("显示", self)
        self.quit_action = QAction("退出", self)
        self.show_action.triggered.connect(self.show_window)
        self.quit_action.triggered.connect(self.close_application)
        tray_menu.addAction(self.show_action)
        tray_menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_form = LoginForm()
    login_form.show()
    logapp = Login2CQUPT()

    sys.exit(app.exec_())
