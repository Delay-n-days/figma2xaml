"""
Figma JSON 到 XAML 转换器 GUI
支持粘贴 JSON，自动压缩并转换为 XAML（仅内容，不含 UserControl 头尾）
"""
import sys
import json
import subprocess
import tempfile
import os
from pathlib import Path
from PySide2.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QSplitter, QMessageBox
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont


class FigmaToXamlConverter(QMainWindow):
    """Figma 到 XAML 转换器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("Figma → XAML 转换器")
        self.setGeometry(100, 100, 1600, 900)  # 增大窗口：1600x900
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题
        title = QLabel("🎨 Figma JSON → WPF XAML 转换器")
        title_font = QFont("Microsoft YaHei UI", 16, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(title)
        
        # 分隔器（左右分栏）
        splitter = QSplitter(Qt.Horizontal)
        
        # === 左侧面板 ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        # 左侧标题
        left_label = QLabel("📥 输入 Figma JSON")
        left_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        left_label.setStyleSheet("color: #34495e; padding: 5px;")
        left_layout.addWidget(left_label)
        
        # JSON 输入框
        self.json_input = QTextEdit()
        self.json_input.setPlaceholderText(
            "在此粘贴 Figma JSON 数据...\n\n"
            "提示：\n"
            "1. 从 Figma 导出 JSON\n"
            "2. Ctrl+V 粘贴到此处\n"
            "3. 点击 '转换' 按钮"
        )
        self.json_input.setFont(QFont("Consolas", 11))  # 增大字体：11
        self.json_input.setMinimumHeight(600)  # 设置最小高度
        self.json_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                background-color: #ecf0f1;
            }
            QTextEdit:focus {
                border: 2px solid #3498db;
                background-color: white;
            }
        """)
        left_layout.addWidget(self.json_input)
        
        # 左侧按钮
        left_buttons = QHBoxLayout()
        
        self.clear_input_btn = QPushButton("🗑️ 清空")
        self.clear_input_btn.setFont(QFont("Microsoft YaHei UI", 10))
        self.clear_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        self.clear_input_btn.clicked.connect(self.clear_input)
        left_buttons.addWidget(self.clear_input_btn)
        
        self.paste_btn = QPushButton("📋 粘贴")
        self.paste_btn.setFont(QFont("Microsoft YaHei UI", 10))
        self.paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        left_buttons.addWidget(self.paste_btn)
        
        left_layout.addLayout(left_buttons)
        
        splitter.addWidget(left_panel)
        
        # === 中间转换按钮 ===
        # 注：实际放在右侧面板上方
        
        # === 右侧面板 ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # 右侧标题和转换按钮
        right_header = QHBoxLayout()
        
        right_label = QLabel("📤 输出 XAML 代码")
        right_label.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        right_label.setStyleSheet("color: #34495e; padding: 5px;")
        right_header.addWidget(right_label)
        
        right_header.addStretch()
        
        # 转换按钮（放在右侧标题栏）
        self.convert_btn = QPushButton("⚡ 转 换")
        self.convert_btn.setFont(QFont("Microsoft YaHei UI", 12, QFont.Bold))
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.convert_btn.clicked.connect(self.convert_json_to_xaml)
        right_header.addWidget(self.convert_btn)
        
        right_layout.addLayout(right_header)
        
        # XAML 输出框
        self.xaml_output = QTextEdit()
        self.xaml_output.setReadOnly(True)
        self.xaml_output.setPlaceholderText(
            "转换后的 XAML 代码将显示在此...\n\n"
            "仅包含内容，不含 <UserControl> 头尾"
        )
        self.xaml_output.setFont(QFont("Consolas", 9))  # 增大字体：11
        self.xaml_output.setMinimumHeight(600)  # 设置最小高度
        self.xaml_output.setStyleSheet("""
            QTextEdit {
                border: 2px solid #27ae60;
                border-radius: 5px;
                padding: 10px;
                background-color: #e8f8f5;
            }
        """)
        right_layout.addWidget(self.xaml_output)
        
        # 右侧按钮
        right_buttons = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 复制 XAML")
        self.copy_btn.setFont(QFont("Microsoft YaHei UI", 10))
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        right_buttons.addWidget(self.copy_btn)
        
        self.clear_output_btn = QPushButton("🗑️ 清空")
        self.clear_output_btn.setFont(QFont("Microsoft YaHei UI", 10))
        self.clear_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7a7b;
            }
        """)
        self.clear_output_btn.clicked.connect(self.clear_output)
        right_buttons.addWidget(self.clear_output_btn)
        
        right_layout.addLayout(right_buttons)
        
        splitter.addWidget(right_panel)
        
        # 设置分隔器比例（左:右 = 1:1）
        splitter.setSizes([800, 800])  # 增大分隔区域
        
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.status_label = QLabel("💡 就绪 - 等待输入 JSON")
        self.status_label.setFont(QFont("Microsoft YaHei UI", 9))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        main_layout.addWidget(self.status_label)
        
    def clear_input(self):
        """清空输入"""
        self.json_input.clear()
        self.update_status("📭 已清空输入", "info")
        
    def clear_output(self):
        """清空输出"""
        self.xaml_output.clear()
        self.update_status("📭 已清空输出", "info")
        
    def paste_from_clipboard(self):
        """从剪贴板粘贴"""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.json_input.setPlainText(text)
            self.update_status("✅ 已粘贴 JSON 数据", "success")
        else:
            self.update_status("⚠️ 剪贴板为空", "warning")
            
    def copy_to_clipboard(self):
        """复制到剪贴板"""
        text = self.xaml_output.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.update_status("✅ XAML 已复制到剪贴板", "success")
        else:
            self.update_status("⚠️ 没有可复制的内容", "warning")
            
    def update_status(self, message, status_type="info"):
        """更新状态栏"""
        colors = {
            "info": "#3498db",
            "success": "#27ae60",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        color = colors.get(status_type, "#7f8c8d")
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 5px;
                font-weight: bold;
            }}
        """)
        
    def convert_json_to_xaml(self):
        """转换 JSON 到 XAML - 调用现有脚本"""
        json_text = self.json_input.toPlainText().strip()
        
        if not json_text:
            self.update_status("❌ 请先输入 Figma JSON 数据", "error")
            QMessageBox.warning(self, "输入为空", "请先粘贴 Figma JSON 数据！")
            return
        
        try:
            self.update_status("⏳ 正在处理...", "info")
            QApplication.processEvents()  # 刷新 UI
            
            # 1. 验证 JSON 格式
            try:
                json_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                self.update_status(f"❌ JSON 格式错误: {str(e)}", "error")
                QMessageBox.critical(self, "JSON 错误", f"JSON 格式不正确：\n{str(e)}")
                return
            
            # 2. 创建临时文件
            temp_dir = tempfile.gettempdir()
            input_json = os.path.join(temp_dir, "figma_input_temp.json")
            compressed_json = os.path.join(temp_dir, "figma_compressed_temp.json")
            output_xaml = os.path.join(temp_dir, "figma_output_temp.xaml")
            
            # 保存输入 JSON
            with open(input_json, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            self.update_status("⏳ 步骤 1/3: 压缩 JSON...", "info")
            QApplication.processEvents()
            
            # 3. 调用压缩脚本（subprocess 方式，不修改原脚本）
            compress_script = Path(__file__).parent / "figma_compressor.py"
            result = subprocess.run(
                [sys.executable, str(compress_script), input_json, compressed_json],
                capture_output=True,
                text=True,
                errors='ignore'  # 忽略编码错误
            )
            
            if result.returncode != 0:
                self.update_status("❌ 压缩失败", "error")
                QMessageBox.critical(self, "压缩错误", f"压缩失败：\n{result.stderr}")
                return
            
            self.update_status("⏳ 步骤 2/3: 转换为 XAML...", "info")
            QApplication.processEvents()
            
            # 4. 调用转换脚本（subprocess 方式，不修改原脚本）
            convert_script = Path(__file__).parent / "figma_to_xaml_v2.py"
            
            # 修改 figma_to_xaml.py 使其接受命令行参数
            # 这里暂时用 subprocess 调用，输入输出都是文件
            result = subprocess.run(
                [sys.executable, str(convert_script), compressed_json, output_xaml],
                capture_output=True,
                text=True,
                errors='ignore',  # 忽略编码错误
                cwd=str(Path(__file__).parent)
            )
            
            if result.returncode != 0 and not os.path.exists(output_xaml):
                self.update_status("❌ 转换失败", "error")
                QMessageBox.critical(self, "转换错误", f"转换失败：\n{result.stderr}")
                return
            
            self.update_status("⏳ 步骤 3/3: 提取内容...", "info")
            QApplication.processEvents()
            
            # 5. 读取生成的 XAML 并提取内容（去掉头尾）
            if os.path.exists(output_xaml):
                with open(output_xaml, 'r', encoding='utf-8') as f:
                    xaml_content = f.read()
            else:
                self.update_status("❌ 未生成 XAML 文件", "error")
                QMessageBox.critical(self, "错误", "未找到生成的 XAML 文件")
                return
            
            # 提取 <UserControl> 和 </UserControl> 之间的内容
            xaml_body = self.extract_xaml_body(xaml_content)
            
            # 6. 显示结果
            self.xaml_output.setPlainText(xaml_body)
            self.update_status("✅ 转换成功！", "success")
            
            # 7. 清理临时文件
            for temp_file in [input_json, compressed_json, output_xaml]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                    
        except Exception as e:
            self.update_status(f"❌ 转换失败: {str(e)}", "error")
            QMessageBox.critical(self, "转换错误", f"转换过程出错：\n{str(e)}")
            
    def extract_xaml_body(self, xaml_content):
        """提取 XAML 主体内容（去掉 UserControl 头尾）"""
        lines = xaml_content.split('\n')
        
        # 找到第一个非 UserControl 标签的行
        start_index = 0
        end_index = len(lines)
        
        in_usercontrol_header = True
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 跳过 UserControl 开始标签
            if in_usercontrol_header:
                if stripped.startswith('<') and not stripped.startswith('</UserControl>'):
                    if not stripped.startswith('<UserControl'):
                        start_index = i
                        in_usercontrol_header = False
                elif stripped.endswith('>') and '<UserControl' in line:
                    # UserControl 标签可能多行
                    start_index = i + 1
                    in_usercontrol_header = False
            
            # 找到结束标签
            if stripped == '</UserControl>':
                end_index = i
                break
        
        # 提取主体内容
        body_lines = lines[start_index:end_index]
        
        # 移除多余的缩进
        if body_lines:
            # 找到最小缩进
            min_indent = float('inf')
            for line in body_lines:
                if line.strip():  # 跳过空行
                    indent = len(line) - len(line.lstrip())
                    min_indent = min(min_indent, indent)
            
            # 移除最小缩进
            if min_indent != float('inf') and min_indent > 0:
                body_lines = [line[min_indent:] if len(line) > min_indent else line 
                             for line in body_lines]
        
        return '\n'.join(body_lines).strip()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = FigmaToXamlConverter()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
