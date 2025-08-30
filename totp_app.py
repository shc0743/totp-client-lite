import sys
import json
import os
import urllib.parse
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QComboBox, QTextEdit, QPushButton, 
                            QProgressBar, QLabel, QMessageBox, QFrame)
from PyQt5.QtCore import QTimer, Qt, QMimeData
from PyQt5.QtGui import QFont, QDrag, QPalette, QColor, QIcon
import pyotp
    
class TOTPApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TOTP 验证码生成器")
        self.setWindowIcon(QIcon("totp_icon.png"))
        self.setFixedSize(450, 280)
        
        # 初始化变量
        self.entries = []
        self.current_totp = None
        self.preferences_file = "preferences.json"
        self.secrets_file = "secrets.txt"
        self.init_done = False
        
        # 设置应用程序样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
        # 创建UI
        self.init_ui()
        
        # 加载secrets和preferences
        self.load_secrets()
        self.load_preferences()
        
        # 设置定时器更新TOTP
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_totp_display)
        self.timer.start(100)  # 每100毫秒更新一次以获得更流畅的进度条
        self.init_done = True

    def init_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 账户选择
        account_layout = QHBoxLayout()
        account_label = QLabel("选择账户:")
        account_label.setFont(QFont("Arial", 10, QFont.Bold))
        account_layout.addWidget(account_label)
        
        self.account_combo = QComboBox()
        self.account_combo.setFont(QFont("Arial", 10))
        self.account_combo.setMinimumHeight(30)
        self.account_combo.currentIndexChanged.connect(self.account_changed)
        account_layout.addWidget(self.account_combo)
        
        layout.addLayout(account_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #dee2e6;")
        layout.addWidget(separator)
        
        # TOTP显示和复制按钮
        totp_layout = QHBoxLayout()
        
        self.totp_entry = QTextEdit()
        self.totp_entry.setMaximumHeight(40)
        self.totp_entry.setLineWrapMode(QTextEdit.NoWrap)
        self.totp_entry.setStyleSheet("QTextEdit { padding-top: 5px; background-color: white; text-align: center; }")
        totp_layout.addWidget(self.totp_entry)
        
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setFont(QFont("Arial", 10))
        self.copy_btn.setMinimumHeight(40)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        totp_layout.addWidget(self.copy_btn)
        
        layout.addLayout(totp_layout)
        
        # 剩余时间进度条和标签
        time_layout = QVBoxLayout()
        
        self.time_progress = QProgressBar()
        self.time_progress.setRange(0, 300)
        self.time_progress.setTextVisible(False)
        self.time_progress.setMinimumHeight(10)
        time_layout.addWidget(self.time_progress)
        
        self.time_label = QLabel("30秒")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 10))
        time_layout.addWidget(self.time_label)
        
        layout.addLayout(time_layout)
        
        # 添加提示文本
        hint_label = QLabel("提示: 您可以选中验证码并直接拖拽到其他应用中使用")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setFont(QFont("Arial", 9))
        hint_label.setStyleSheet("color: #6c757d;")
        layout.addWidget(hint_label)

    def parse_otpauth_uri(self, uri):
        """解析otpauth URI并返回相关信息"""
        try:
            # 解码URL编码的部分
            decoded_uri = urllib.parse.unquote(uri)
            
            # 解析URI
            if not decoded_uri.startswith('otpauth://totp/'):
                return None
                
            # 提取基础部分
            base_part = decoded_uri.split('?', 1)
            if len(base_part) < 2:
                return None
                
            path_part = base_part[0].replace('otpauth://totp/', '')
            query_part = base_part[1]
            
            # 解析路径部分
            if ':' in path_part:
                issuer, account_name = path_part.split(':', 1)
            else:
                issuer = ""
                account_name = path_part
                
            # 解析查询参数
            params = urllib.parse.parse_qs(query_part)
            secret = params.get('secret', [''])[0]
            issuer_from_params = params.get('issuer', [''])[0]
            
            # 优先使用参数中的issuer
            if issuer_from_params:
                issuer = issuer_from_params
                
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
            QMessageBox.critical(self, "错误", f"找不到 {self.secrets_file} 文件")
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
            QMessageBox.critical(self, "错误", f"{self.secrets_file} 中没有有效的TOTP配置")
            return
            
        self.account_combo.addItems(account_names)

    def load_preferences(self):
        """加载用户偏好设置"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    last_account = preferences.get('last_account', '')
                    
                    index = self.account_combo.findText(last_account)
                    if index >= 0:
                        self.account_combo.setCurrentIndex(index)
                        # 手动触发账户选择事件
                        self.on_account_select(last_account)
            except Exception as e:
                print(f"加载偏好设置时出错: {e}")
        
        # 如果没有选择任何账户，选择第一个
        if self.account_combo.currentIndex() == -1 and self.account_combo.count() > 0:
            self.account_combo.setCurrentIndex(0)
            # 手动触发账户选择事件
            self.on_account_select(self.account_combo.currentText())

    def save_preferences(self):
        """保存用户偏好设置"""
        if not self.init_done:
            return
        try:
            preferences = {
                'last_account': self.account_combo.currentText()
            }
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f)
        except Exception as e:
            print(f"保存偏好设置时出错: {e}")

    def on_account_select(self, account_name):
        """当用户选择不同账户时的处理"""
        # 检查 account_name 是否为 None 或空字符串
        if not account_name or account_name == "":
            return
            
        # 查找对应的secret
        for entry in self.entries:
            if entry['display_name'] == account_name:
                self.current_totp = pyotp.TOTP(entry['secret'])
                break

        # 保存偏好
        self.save_preferences()
        
        # 立即更新TOTP显示
        self.update_totp_display()

    # 添加一个新的信号处理方法来确保偏好保存
    def account_changed(self, index):
        """当用户选择不同账户时的处理（通过索引）"""
        if index >= 0:
            account_name = self.account_combo.itemText(index)
            self.on_account_select(account_name)
            
    def update_totp_display(self):
        """更新TOTP显示内容"""
        if not self.current_totp:
            return
            
        # 生成当前TOTP
        current_code = self.current_totp.now()
        
        # 计算剩余时间
        current_time = datetime.now()
        remaining = 30 - (current_time.second % 30)
        elapsed_ms_in_current_period = (current_time.second % 30) * 1000 + current_time.microsecond // 1000
        remaining_ms = 30000 - elapsed_ms_in_current_period
        progress_value = remaining_ms / 30000.0
        
        # 更新界面
        if self.totp_entry.toPlainText() != current_code:
            self.totp_entry.setText(current_code)
        self.time_progress.setValue(int(progress_value * 300))  # 转换为0-300范围
        self.time_label.setText(f"{remaining}秒")
        
        # 根据剩余时间改变进度条颜色
        if remaining <= 5:
            self.time_progress.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #dc3545;
                    border-radius: 3px;
                }
            """)
        else:
            self.time_progress.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #28a745;
                    border-radius: 3px;
                }
            """)

    def copy_to_clipboard(self):
        """复制TOTP到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.totp_entry.toPlainText())
        
        # 显示提示信息
        self.copy_btn.setText("已复制!")
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("复制"))

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序字体
    font = QFont("Consolas", 13)
    app.setFont(font)
    
    window = TOTPApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()