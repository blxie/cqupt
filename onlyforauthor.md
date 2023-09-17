# cqupt

toolkits for cqupt

## 环境准备（注意 `Powershell` 必须安装！）

-   `Python > 3.0`

```bash
conda create -n test python=3.8
conda activate test
pip install -r requirements.txt
```

-   `PowerShell` 安装（依赖于这个命令行软件）

> 官方文档：https://learn.microsoft.com/zh-cn/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.3#install-powershell-using-winget-recommended

```powershell
winget search Microsoft.PowerShell
winget install --id Microsoft.Powershell --source winget
```

## `WIN` 打包并安装为服务程序

> 打包为 `.exe` 可执行文件，

```bash
pyinstaller.exe --uac-admin --onefile login2cqupt_tiny.py --name Login2CQUPT_tiny --icon="assets/icons/icon.jpg"
pyinstaller.exe --uac-admin --onefile login2cqupt_base.py --name Login2CQUPT_base --icon="assets/icons/icon.jpg"
```

> 作为服务程序进行安装

1. 将生成的 dist/login2cqupt 复制到你的 `APP` 目录下；

2. 下载配置 `nssm` 工具（[下载地址](https://nssm.cc/download)；`nssm` 下载安装好之后，将 `x64/nssm.exe` 的完整路径添加到 系统环境变量的 `PATH` 条目下，

    ![nssm 环境变量设置](assets/nssm_env_path.png)

3. 使用 `nssm` 工具将可执行程序 `login2cqupt.exe` 安装为服务程序，使得可以在后台运行，以及开启自启动；

以管理员身份运行 `CMD/PowerShell`，执行以下命令，

```bash
nssm install login2cqupt  # 安装 login2cqupt 服务程序
# 找到 `APP/login2cqupt/login2cqupt.exe`，并添加以下参数
--account "YOUR_ACCOUNT" --password "YOUR_PASSWD" --operator "移动" --log_path "./cqupt.log" --device "pc" --sleep_time 30

nssm start login2cqupt  # 启动 login2cqupt 服务程序
```

如图示，
![nssm_install](assets/nssm_install.png)

打开 `Windows` 服务，可以看到安装的 `login2cqupt` 的运行状况，也可以在 任务管理器 —— 服务 中进行查看。

## ⚡ 注意

> WiFi 的话要首先连接（自动创建连接配置文件），分配给指定接口的配置文件“CQUPT”

```
%ProgramData%\Microsoft\Wlansvc\Profiles\Interfaces\网卡ID
```

网卡 ID 可通过 [TMAC](https://technitium.com/tmac/) 查看，还可以通过 `TMAC` 更改适配器的 `MAC` 地址，突破网速的限制（可能不太稳定，延迟时高时低）。

> 如果蓝屏，到官方网站手动下载安装最新的网络驱动器！

## 参考文档

> -   tiny 版本参考：https://zhuanlan.zhihu.com/p/300909829

## python 运行的时候就自动获取管理员权限

在 Python 中，要实现程序在运行时自动获取管理员权限，可以通过修改程序的执行方式来实现。具体而言，可以将程序打包为一个特殊类型的可执行文件（.exe），该文件在运行时自动请求管理员权限。

有几种方法可以实现这一点，其中一种是使用 PyInstaller 打包程序，并将 UAC（用户账户控制）权限设置为最高级别。以下是一个示例过程：

1. 确保你已经安装了 PyInstaller，你可以使用以下命令通过 pip 安装：

    ```bash
    pip install pyinstaller
    ```

2. 创建 Python 程序，命名为 `main.py`，并在其中编写你的程序逻辑。

3. 在命令行中，进入包含 `main.py` 的目录，并执行以下命令以使用 PyInstaller 打包程序：

    ```bash
    pyinstaller --uac-admin --onefile login2cqupt.py

    # 以管理员
    nssm install login2cqupt
    ```

    这个命令会使用 PyInstaller 将 `main.py` 打包为一个可执行文件，并将 UAC 权限设置为最高级别。生成的可执行文件将自动请求管理员权限。

4. 打包完成后，你可以在生成的 `dist` 文件夹中找到生成的可执行文件。运行该文件时，系统将自动弹出管理员权限请求对话框。

请注意，请求管理员权限可能会带来系统安全风险。确保你的程序只在必要时请求管理员权限，并遵循最佳实践来确保程序的安全性。此外，用户可能需要以普通用户身份运行可执行文件，以便请求管理员权限的过程生效。如果用户已经以管理员身份运行，请求管理员权限的过程将被跳过。

### 注意

> WiFi 的话要首先连接（自动创建连接配置文件），分配给指定接口的配置文件“CQUPT”

```
%ProgramData%\Microsoft\Wlansvc\Profiles\Interfaces\网卡的ID（可通过TMAC查看）
```

![image](https://github.com/blxie/cqupt/assets/43612290/f205d509-b041-4185-9d16-6bed1cc940d0)

![image](https://github.com/blxie/cqupt/assets/43612290/e4bc5847-2dd5-4951-a485-5febef3efe4f)

![image](https://github.com/blxie/cqupt/assets/43612290/1b0e64c2-453d-4ff9-831d-be097edabff6)

chatgpt 指令，

```
windows下python守护进程创建
服务停止有问题，不能停止该服务
python demo.py install无任何反应
SvcRemove移除服务还没实现

windows服务模块强制刷新
```

## 参考文献

> -   [global 的用法](https://blog.csdn.net/TracelessLe/article/details/123691579)

命令行命令，

```bash
netsh interface show interface
netsh interface show interface "以太网"
netsh wlan connect name=CQUPT ssid=CQUPT
```

`time.sleep()` 何时用，值设置为多少很重要，直接影响最终能否运行！

> 如果蓝屏，到官方网站手动下载安装最新的网络驱动器！

## Git

`dev -> main`

```bash
$env:https_proxy="http://127.0.0.1:10809"

git init
git branch -M main
git remote add origin https://github.com/blxie/cqupt.git

git add .\README.md
git status
git commit -m "init README"
git push -u origin main

git branch dev
git checkout dev
# 将 dev 添加到远程仓库的分支中，隶属于 main 分支
# 在 dev 上进行开发，只有在 milestone 才合并到 main！然后再推送到远程仓库
git push origin dev

## 同步 main，然后开发
git pull origin main
git checkout dev

git add xxx
git commit -m ""
git push -u origin main

## 将 main_ 合并到 main
git checkout main
git merge --allow-unrelated-histories main
## git merge 之后不用再 commit！直接进行 push 推送即可！
git push -u origin main
```

> 注意：`merger` 时不能 `commit --amend`，如果要在上一级修改，直接切换到这个分支 e.g. `main`，然后在 `main` 上直接进行 `--amend` 操作！

```bash
git checkout dev
git status
git add -u
git commit -m "milestone! with retry"
git push -u origin dev

git checkout main
git merge dev
git push -u origin main
git tag -a v1.0 -m "Perfect!"
git tag
git push origin v1.0
```

## 打包

```bash
pyinstaller.exe --uac-admin --onefile login2cqupt.py
pyinstaller.exe --uac-admin --onefile app.py --add-data="icons;icons" --noconsole

--account "YOUR_ACCOUNT" --password "YOUR_PASSWD" --operator "移动" --log_path "./cqupt.log" --device "pc" --sleep_time 30
```
