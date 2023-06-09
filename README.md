# cqupt
toolkits for cqupt

## python运行的时候就自动获取管理员权限

在 Python 中，要实现程序在运行时自动获取管理员权限，可以通过修改程序的执行方式来实现。具体而言，可以将程序打包为一个特殊类型的可执行文件（.exe），该文件在运行时自动请求管理员权限。

有几种方法可以实现这一点，其中一种是使用 PyInstaller 打包程序，并将 UAC（用户账户控制）权限设置为最高级别。以下是一个示例过程：

1. 确保你已经安装了 PyInstaller，你可以使用以下命令通过 pip 安装：

   ```bash
   pip install pyinstaller
   ```

2. 创建 Python 程序，命名为 `main.py`，并在其中编写你的程序逻辑。

3. 在命令行中，进入包含 `main.py` 的目录，并执行以下命令以使用 PyInstaller 打包程序：

   ```bash
   pyinstaller --uac-admin login2cqupt.py
   
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


chatgpt指令，

```
windows下python守护进程创建
服务停止有问题，不能停止该服务
python demo.py install无任何反应
SvcRemove移除服务还没实现

windows服务模块强制刷新
```

## 参考文献
> - [global 的用法](https://blog.csdn.net/TracelessLe/article/details/123691579)



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

