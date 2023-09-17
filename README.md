# cqupt

Auto-login toy for CQUPT.

## 使用方法

下载可执行文件
方法1：下载 `dist` 目录中的所有文件
方法2：通过 `release` 下载，

1. 修改配置文件 `config.yaml`，主要是账号和密码。

2. 运行 `Login2CQUPT_tiny.exe` 或者 `Login2CQUPT_base.exe`
    - `tiny` 基本够用；
    - `base` 增加网络适配器的禁用启用等功能，增加了更加复杂的逻辑，适用于更加复杂的场景。

如果需要将应用程序制作为守护进程，注册为 Windows 的一个服务程序，请按照以下操作完成。

## `WIN` 打包并安装为服务程序

> 作为服务程序进行安装

1. 将生成的 `.exe` 以及 `config.yaml` 复制到你的 `APP` 目录下；

2. 下载配置 `nssm` 工具（[下载地址](https://nssm.cc/download)；`nssm` 下载安装好之后，将 `x64/nssm.exe` 的完整路径添加到 系统环境变量的 `PATH` 条目下，

    ![nssm 环境变量设置](assets/nssm_env_path.png)

3. 使用 `nssm` 工具将可执行程序 `login2cqupt.exe` 安装为服务程序，使得可以在后台运行，以及开启自启动；

以管理员身份运行 `CMD/PowerShell`，执行以下命令，

```bash
nssm install login2cqupt  # 安装 login2cqupt 服务程序
# 找到 `APP/login2cqupt/Login2CQUPT_base/tiny.exe`

nssm start login2cqupt  # 启动 login2cqupt 服务程序
```

如图示，
![nssm_install](assets/nssm_install.png)
> 【注意】：该版本不需要上图的第二步操作！不需要增加额外的参数，直接在配置文件中进行修改。

打开 `Windows` 服务，可以看到安装的 `login2cqupt` 的运行状况，也可以在 任务管理器 —— 服务 中进行查看。
