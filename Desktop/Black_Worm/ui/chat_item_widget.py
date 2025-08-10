
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import Config

class ChatItemWidget(QWidget):
    
    chat_selected = pyqtSignal(str)  # conversation_id
    chat_deleted = pyqtSignal(str)   # conversation_id
    
    def __init__(self, conversation_id, title, updated_at):
        super().__init__()
        self.conversation_id = conversation_id
        self.title = title
        self.updated_at = updated_at
        self.setup_ui()
    
    def setup_ui(self):
        container = QFrame()
        container.setObjectName("chatItemContainer")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(15, 12, 12, 12)
        container_layout.setSpacing(10)
        
        self.title_label = QLabel()
        self.title_label.setObjectName("chatTitleLabel")
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_label.setWordWrap(False)
        
        display_title = self.truncate_title(self.title, 20)
        self.title_label.setText(display_title)
        
        self.title_label.mousePressEvent = self.on_title_clicked
        self.title_label.setCursor(Qt.PointingHandCursor)
        
        self.delete_btn = QPushButton("×")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setFixedSize(28, 28)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setToolTip("Delete conversation")
        
        container_layout.addWidget(self.title_label)
        container_layout.addWidget(self.delete_btn)
        
        main_layout.addWidget(container)
        
        self.apply_styles()
    
    def truncate_title(self, title, max_length):
        if len(title) <= max_length:
            return title
        
        truncated = title[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:
            return title[:last_space] + "..."
        else:
            return title[:max_length] + "..."
    
    def apply_styles(self):
        self.setStyleSheet(f"""
            QFrame#chatItemContainer {{
                background: {Config.CARD_GRADIENT};
                border: 1px solid rgba(0, 245, 255, 0.2);
                border-radius: 12px;
                margin: 2px 0px;
                min-height: 50px;
            }}
            
            QFrame#chatItemContainer:hover {{
                background: {Config.TEAL_GRADIENT};
                border: 2px solid rgba(0, 245, 255, 0.6);
            }}
            
            QLabel#chatTitleLabel {{
                color: {Config.TEXT_COLOR};
                font-size: {Config.FONT_SIZE_NORMAL}px;
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
            
            QFrame#chatItemContainer:hover QLabel#chatTitleLabel {{
                color: #1a1a1a;
                font-weight: 600;
            }}
            
            QPushButton#deleteButton {{
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 14px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 18px;
                font-weight: bold;
                font-family: '{Config.FONT_FAMILY}';
                text-align: center;
            }}
            
            QPushButton#deleteButton:hover {{
                background: rgba(255, 50, 50, 0.9);
                border: 2px solid #ff3333;
                color: white;
                font-size: 20px;
            }}
            
            QPushButton#deleteButton:pressed {{
                background: rgba(200, 0, 0, 0.95);
                border: 2px solid #cc0000;
                color: white;
            }}
            
            QFrame#chatItemContainer:hover QPushButton#deleteButton {{
                background: rgba(255, 255, 255, 0.25);
                border: 2px solid rgba(255, 255, 255, 0.5);
                color: white;
            }}
        """)
    
    def on_title_clicked(self, event):
        if event.button() == Qt.LeftButton:
            self.chat_selected.emit(self.conversation_id)
    
    def on_delete_clicked(self):
        self.chat_deleted.emit(self.conversation_id)
    
    def set_selected(self, selected):
        if selected:
            self.setStyleSheet(self.styleSheet() + f"""
                QFrame#chatItemContainer {{
                    background: {Config.ACCENT_GRADIENT} !important;
                    border: 2px solid {Config.ACCENT_COLOR} !important;
                }}
                QLabel#chatTitleLabel {{
                    color: #1a1a1a !important;
                    font-weight: 700 !important;
                }}
            """)
        else:
            self.apply_styles()
    
    def update_title(self, new_title):
        self.title = new_title
        display_title = self.truncate_title(new_title, 20)
        self.title_label.setText(display_title)
    
    def update_timestamp(self, new_timestamp):
        self.updated_at = new_timestamp