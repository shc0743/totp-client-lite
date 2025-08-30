Simple TOTP (Time-based One-Time Password) Application based on PyOTP

# Features

- Lightweight
- Portable, able to put into a USB drive
- Local, no data upload
- No network connection required
- Drag and drop instead of copy

# How to use

1. Download the code as .zip and expand it
2. Run the `create_runtime.cmd`. By doing this, a runtime environment will be created automatically.
3. Put your secrets to `secrets.txt`.
4. Run `app.cmd`.
5. The TOTP codes will be generated automatically.

# Secrets format

The secrets file should be in the following format:

```
otpauth://totp/Microsoft:YourName%40outlook.com?secret=YOURSECRET&issuer=Microsoft
otpauth://totp/Google:YourName%40gmail.com?secret=YOURSECRETHERE&issuer=Google
otpauth://totp/YourService:YourName?secret=YOURSECRET&issuer=YourService
```

For most cases, you can just "backup" in your current TOTP app as "Plain Text" to get the file.

# Important notes

**The secrets.txt is NOT encrypted by the application**.

To protect your secrets, please:
- Either enable EFS (Encrypting File System)
- Or put the file into a BitLocker encrypted drive or VeraCrypt volume

# Chinese explaination

## 特性

- 轻量级：应用体积小，资源占用低，运行高效
- 便携化：可存放于U盘中，随时随地使用
- 本地化：所有数据仅存储于本地，无任何数据上传
- 无需联网：完全离线运行，不依赖网络连接

## 使用方法

1. 下载代码压缩包（.zip）并解压
2. 运行 `create_runtime.cmd` 自动创建运行环境（首次使用需执行）
3. 将您的密钥信息存入 `secrets.txt` 文件中
4. 运行 `app.cmd` 启动应用
5. TOTP 验证码将自动生成并显示

## 密钥格式说明

密钥文件需按以下格式编写（每行一个账户）：

```
otpauth://totp/服务商:用户名%40域名?secret=密钥值&issuer=服务商名称
```

例如：
```
otpauth://totp/Microsoft:example%40outlook.com?secret=ABC123&issuer=Microsoft
otpauth://totp/Google:test%40gmail.com?secret=XYZ789&issuer=Google
```

> 提示：大多数TOTP应用都支持将密钥导出为「纯文本格式」，直接导出即可获得符合要求的文件。

## 补充说明

- 运行环境基于 Python
- 请妥善保管 `secrets.txt` 文件，避免密钥信息泄露
- 支持所有符合 TOTP 标准的服务（Google Authenticator/Authy 等兼容）

## 重要提示

**secrets.txt 文件并未经过本应用程序加密处理**。

为保护您的机密信息，请执行以下操作之一：
- 启用EFS（加密文件系统）
- 或将文件存放于经过BitLocker加密的驱动器或VeraCrypt加密卷中

# License

GPL-3.0