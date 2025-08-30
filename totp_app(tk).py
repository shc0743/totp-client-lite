import tkinter as tk
from tkinter import ttk, messagebox
import pyotp
import json
import os
import re
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime

class TOTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TOTP 验证码生成器")
        self.root.resizable(False, False)
        
        # 初始化变量
        self.entries = []
        self.current_totp = None
        self.preferences_file = "preferences.json"
        self.secrets_file = "secrets.txt"
        
        # 创建界面
        self.create_widgets()
        
        # 加载secrets和preferences
        self.load_secrets()
        self.load_preferences()
        
        # 开始更新TOTP
        self.update_totp()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 账户选择标签和下拉框
        ttk.Label(main_frame, text="选择账户:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(main_frame, textvariable=self.account_var, state="readonly")
        self.account_combo.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.account_combo.bind('<<ComboboxSelected>>', self.on_account_select)
        
        # TOTP显示和复制按钮
        totp_frame = ttk.Frame(main_frame)
        totp_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.totp_var = tk.StringVar()
        self.totp_entry = ttk.Entry(totp_frame, textvariable=self.totp_var, 
                                   font=("Courier", 14), justify="center", state="readonly")
        self.totp_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.copy_btn = ttk.Button(totp_frame, text="复制", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1)
        
        # 剩余时间进度条
        self.time_remaining_var = tk.IntVar(value=30)
        self.time_progress = ttk.Progressbar(main_frame, variable=self.time_remaining_var, 
                                           maximum=30, mode='determinate')
        self.time_progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 剩余时间标签
        self.time_label = ttk.Label(main_frame, text="30秒")
        self.time_label.grid(row=4, column=0, columnspan=2, pady=(5, 0))
        
        # 配置列权重
        main_frame.columnconfigure(0, weight=1)
        totp_frame.columnconfigure(0, weight=1)

    def parse_otpauth_uri(self, uri):
        """解析otpauth URI并返回相关信息"""
        try:
            parsed = urlparse(uri)
            if parsed.scheme != 'otpauth' or parsed.netloc != 'totp':
                return None
                
            # 提取路径中的标识符并进行URL解码
            path_parts = parsed.path.split(':')
            account_name = unquote(path_parts[-1].lstrip('/'))
            
            # 提取查询参数
            query_params = parse_qs(parsed.query)
            secret = query_params.get('secret', [''])[0]
            issuer = unquote(query_params.get('issuer', [''])[0]) if query_params.get('issuer') else ''
            
            if not secret:
                return None
                
            # 创建显示名称
            display_name = f"{issuer}:{account_name}" if issuer else account_name
            
            return {
                'display_name': display_name,
                'secret': secret,
                'issuer': issuer,
                'account': account_name
            }
        except Exception as e:
            print(f"解析URI时出错: {e}")
            return None

    def load_secrets(self):
        """从secrets.txt加载TOTP配置"""
        if not os.path.exists(self.secrets_file):
            messagebox.showerror("错误", f"找不到 {self.secrets_file} 文件")
            return
            
        self.entries = []
        account_names = []
        
        with open(self.secrets_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                entry = self.parse_otpauth_uri(line)
                if entry:
                    self.entries.append(entry)
                    account_names.append(entry['display_name'])
        
        if not self.entries:
            messagebox.showerror("错误", f"{self.secrets_file} 中没有有效的TOTP配置")
            return
            
        self.account_combo['values'] = account_names

    def load_preferences(self):
        """加载用户偏好设置"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    last_account = preferences.get('last_account', '')
                    if last_account in self.account_combo['values']:
                        self.account_combo.set(last_account)
                        self.on_account_select(None)
            except Exception as e:
                print(f"加载偏好设置时出错: {e}")
        
        # 如果没有选择任何账户，选择第一个
        if not self.account_var.get() and self.entries:
            self.account_combo.current(0)
            self.on_account_select(None)

    def save_preferences(self):
        """保存用户偏好设置"""
        try:
            preferences = {
                'last_account': self.account_var.get()
            }
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f)
        except Exception as e:
            print(f"保存偏好设置时出错: {e}")

    def on_account_select(self, event):
        """当用户选择不同账户时的处理"""
        selected = self.account_var.get()
        if not selected:
            return
            
        # 查找对应的secret
        for entry in self.entries:
            if entry['display_name'] == selected:
                self.current_totp = pyotp.TOTP(entry['secret'])
                break
                
        # 保存偏好
        self.save_preferences()
        
        # 立即更新TOTP显示
        self.update_totp_display()

    def update_totp(self):
        """更新TOTP显示"""
        self.update_totp_display()
        self.root.after(1000, self.update_totp)  # 每秒更新一次

    def update_totp_display(self):
        """更新TOTP显示内容"""
        if not self.current_totp:
            return
            
        # 生成当前TOTP
        current_code = self.current_totp.now()
        
        # 计算剩余时间
        current_time = datetime.now()
        remaining = 30 - (current_time.second % 30)
        if remaining == 0:
            remaining = 30
            
        # 更新界面
        self.totp_var.set(current_code)
        self.time_remaining_var.set(remaining)
        self.time_label.config(text=f"{remaining}秒")

    def copy_to_clipboard(self):
        """复制TOTP到剪贴板"""
        if self.totp_var.get():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.totp_var.get())
            self.root.update()  # 保持剪贴板内容
            
            # 显示提示信息
            self.copy_btn.config(text="已复制!")
            self.root.after(2000, lambda: self.copy_btn.config(text="复制"))

def main():
    root = tk.Tk()
    app = TOTPApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()