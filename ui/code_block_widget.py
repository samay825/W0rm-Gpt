
import re
import hashlib
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QApplication, QTextEdit, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import Config

class CodeBlockWidget(QFrame):
    
    def __init__(self, code_content, language=""):
        super().__init__()
        self.code_content = code_content.strip()
        self.language = language
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)
        
        if self.language:
            lang_label = QLabel(self.language.upper())
            lang_label.setStyleSheet(f"""
                QLabel {{
                    color: #00f5ff;
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 600;
                    font-family: '{Config.FONT_FAMILY}';
                    background: transparent;
                    padding: 2px 6px;
                    border-radius: 4px;
                    border: 1px solid rgba(0, 245, 255, 0.3);
                }}
            """)
            header_layout.addWidget(lang_label)
        
        header_layout.addStretch()
        
        self.copy_button = QPushButton("📋 Copy")
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00f5ff;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background: rgba(0, 245, 255, 0.2);
                border: 1px solid rgba(0, 245, 255, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(0, 245, 255, 0.3);
                border: 1px solid rgba(0, 245, 255, 0.7);
            }}
        """)
        self.copy_button.clicked.connect(self.copy_code)
        header_layout.addWidget(self.copy_button)
        
        self.code_label = QLabel(self.code_content)
        self.code_label.setWordWrap(True)
        self.code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.code_label.setFont(QFont("Consolas", 12))
        self.code_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: #e8f4fd;
                font-family: 'Consolas', 'Fira Code', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.4;
                padding: 12px 16px;
                white-space: pre-wrap;
            }}
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.code_label)
        
        self.setLayout(layout)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #1a1a2e, stop:0.3 #16213e, stop:0.7 #0f3460, stop:1 #1a1a2e);
                border: 2px solid rgba(0, 245, 255, 0.4);
                border-radius: 12px;
                margin: 8px 0px;
            }}
            QFrame:hover {{
                border: 2px solid rgba(0, 245, 255, 0.6);
            }}
        """)
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(0)
    
    def copy_code(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_content)
        
        original_text = self.copy_button.text()
        self.copy_button.setText("✅ Copied!")
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 230, 118, 0.2);
                border: 1px solid rgba(0, 230, 118, 0.5);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00e676;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
        """)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.reset_copy_button(original_text))
    
    def reset_copy_button(self, original_text):
        self.copy_button.setText(original_text)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 245, 255, 0.1);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
                font-size: {Config.FONT_SIZE_SMALL}px;
                color: #00f5ff;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
            }}
            QPushButton:hover {{
                background: rgba(0, 245, 255, 0.2);
                border: 1px solid rgba(0, 245, 255, 0.5);
            }}
            QPushButton:pressed {{
                background: rgba(0, 245, 255, 0.3);
                border: 1px solid rgba(0, 245, 255, 0.7);
            }}
        """)


class EnhancedMessageWidget(QWidget):
    
    def __init__(self, sender, content, timestamp):
        super().__init__()
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 5, 15, 5)
        main_layout.setSpacing(0)
        
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(15, 12, 15, 12)
        bubble_layout.setSpacing(8)
        
        self.parse_and_add_content(bubble_layout)
        
        time_label = QLabel(self.format_timestamp())
        time_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        bubble_layout.addWidget(time_label)
        
        bubble_container.setMaximumWidth(500)
        
        if self.sender == 'user':
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
            
            bubble_container.setStyleSheet(f"""
                QWidget {{
                    background: {Config.ACCENT_GRADIENT};
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }}
            """)
            
            time_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba(26, 26, 26, 0.7);
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 500;
                    background: transparent;
                }}
            """)
            time_label.setAlignment(Qt.AlignRight)
            
        else:
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()
            
            bubble_container.setStyleSheet(f"""
                QWidget {{
                    background: rgba(255, 255, 255, 0.15);
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }}
            """)
            
            time_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.7);
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 500;
                    background: transparent;
                }}
            """)
            time_label.setAlignment(Qt.AlignLeft)
        
        self.setLayout(main_layout)
    
    def parse_and_add_content(self, layout):
        code_block_pattern = r'```(?:(\w+)\s*)?\n?(.*?)```'
        parts = re.split(code_block_pattern, self.content, flags=re.DOTALL)
        
        i = 0
        while i < len(parts):
            if i % 3 == 0:
                text = parts[i].strip()
                if text:
                    from utils.text_formatter import TextFormatter
                    formatted_text = TextFormatter.format_with_multiple_styles(text, self.sender)
                    
                    text_label = QLabel(formatted_text)
                    text_label.setWordWrap(True)
                    text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    text_label.setTextFormat(Qt.RichText)
                    text_label.setMaximumWidth(450)
                    
                    if self.sender == 'user':
                        text_label.setStyleSheet(f"""
                            QLabel {{
                                color: #1a1a1a;
                                font-size: {Config.FONT_SIZE_MEDIUM}px;
                                line-height: 1.4;
                                font-weight: 600;
                                font-family: '{Config.FONT_FAMILY}';
                                background: transparent;
                                padding: 2px 0px;
                            }}
                        """)
                    else:
                        text_label.setStyleSheet(f"""
                            QLabel {{
                                color: white;
                                font-size: {Config.FONT_SIZE_MEDIUM}px;
                                line-height: 1.4;
                                font-weight: 600;
                                font-family: '{Config.FONT_FAMILY}';
                                background: transparent;
                                padding: 2px 0px;
                            }}
                        """)
                    
                    layout.addWidget(text_label)
            
            elif i % 3 == 1:
                language = parts[i] if parts[i] else ""
                code_content = parts[i + 1] if i + 1 < len(parts) else ""
                
                if code_content.strip():
                    code_widget = CodeBlockWidget(code_content, language)
                    layout.addWidget(code_widget)
                
                i += 1
            
            i += 1
    
    def format_timestamp(self):
        try:
            if isinstance(self.timestamp, str):
                from datetime import datetime
                dt = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            else:
                dt = self.timestamp
            
            from datetime import datetime
            now = datetime.now()
            if dt.date() == now.date():
                return dt.strftime("%H:%M")
            else:
                return dt.strftime("%m/%d %H:%M")
        except:
            return "Now"