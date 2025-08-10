from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QWidget,
                             QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from datetime import datetime
from utils.config import Config
from utils.api_client import APIClient
from utils.session_manager import SessionManager


class AccountInfoWorker(QThread):
    finished = pyqtSignal(bool, dict)
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.session_manager = SessionManager()
    
    def run(self):
        try:
            local_data = self.session_manager.get_user_data()
            if not local_data:
                self.finished.emit(False, {'error': 'No local session found'})
                return
            
            success, response = self.session_manager.validate_session_with_server()
            
            if success:
                account_data = response.get('account', {})
                self.finished.emit(True, account_data)
            else:
                self.finished.emit(False, response)
                
        except Exception as e:
            self.finished.emit(False, {'error': str(e)})


class AccountInfoDialog(QDialog):
    """Dialog to display user account information"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Account Information")
        self.setFixedSize(620, 650)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.account_data = {}
        self.worker = None
        self.drag_position = None
        
        self.setup_ui()
        self.apply_styles()
        self.load_account_info()
    
    def setup_ui(self):
        main_container = QFrame(self)
        main_container.setGeometry(0, 0, 620, 650)
        main_container.setObjectName("mainContainer")
        
        layout = QVBoxLayout(main_container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)
        
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        self.loading_frame = QFrame()
        self.loading_frame.setObjectName("loadingFrame")
        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setSpacing(15)
        loading_layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setFixedHeight(8)
        loading_layout.addWidget(self.progress_bar)
        
        self.loading_label = QLabel("Loading account information...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        loading_layout.addWidget(self.loading_label)
        
        content_layout.addWidget(self.loading_frame)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("scrollArea")
        self.scroll_area.hide()  # Hidden initially
        
        self.info_widget = QWidget()
        self.info_widget.setObjectName("infoWidget")
        self.info_layout = QVBoxLayout(self.info_widget)
        self.info_layout.setSpacing(15)
        self.info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.info_widget)
        content_layout.addWidget(self.scroll_area)
        
        self.error_frame = QFrame()
        self.error_frame.setObjectName("errorFrame")
        error_layout = QVBoxLayout(self.error_frame)
        error_layout.setSpacing(15)
        error_layout.setContentsMargins(20, 20, 20, 20)
        
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        error_layout.addWidget(self.error_label)
        
        retry_btn = QPushButton("🔄 Retry")
        retry_btn.setObjectName("retryButton")
        retry_btn.clicked.connect(self.load_account_info)
        retry_btn.setFixedHeight(40)
        error_layout.addWidget(retry_btn)
        
        self.error_frame.hide()
        content_layout.addWidget(self.error_frame)
        
        
        layout.addWidget(content_frame)
    
    def create_title_bar(self):
        """Create custom title bar"""
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(50)
        title_bar.mousePressEvent = self.title_bar_mouse_press
        title_bar.mouseMoveEvent = self.title_bar_mouse_move
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 15, 0)
        title_layout.setSpacing(10)
        
        title_container = QHBoxLayout()
        
        icon_label = QLabel("👤")
        icon_label.setFont(QFont(Config.FONT_FAMILY, 16))
        title_container.addWidget(icon_label)
        
        title_label = QLabel("Account Information")
        title_label.setFont(QFont(Config.FONT_FAMILY, 16, QFont.Bold))
        title_label.setObjectName("titleLabel")
        title_container.addWidget(title_label)
        
        title_layout.addLayout(title_container)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("titleCloseButton")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.accept)
        title_layout.addWidget(close_btn)
        
        return title_bar
    
    def title_bar_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def title_bar_mouse_move(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def apply_styles(self):
        self.setStyleSheet(f"""
            /* Main Container */
            QFrame#mainContainer {{
                background: solid black;
                background-color: #000000;
                border: 3px solid;
                border-image: linear-gradient(45deg, #00f5ff, #8a2be2, #00bcd4, #ff4081) 1;
                border-radius: 20px;
            }}
            
            /* Title Bar */
            QFrame#titleBar {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00f5ff, 
                    stop:0.3 #00bcd4, 
                    stop:0.7 #8a2be2, 
                    stop:1 #ff4081);
                border-radius: 17px 17px 0px 0px;
                border-bottom: 2px solid rgba(255, 255, 255, 0.2);
            }}
            
            QLabel#titleLabel {{
                color: white;
                font-weight: bold;
                font-size: 16px;
            }}
            
            QPushButton#titleCloseButton {{
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton#titleCloseButton:hover {{
                background: rgba(255, 0, 0, 0.7);
            }}
            
            QPushButton#titleCloseButton:pressed {{
                background: rgba(200, 0, 0, 0.8);
            }}
            
            /* Content Frame */
            QFrame#contentFrame {{
                background: #000000;
                border: none;
                border-radius: 0px 0px 17px 17px;
            }}
            
            /* Loading Frame */
            QFrame#loadingFrame {{
                background: #000000;
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 15px;
                margin: 10px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.1);
                color: {Config.TEXT_COLOR};
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background: {Config.ACCENT_GRADIENT};
                border-radius: 4px;
            }}
            
            /* Scroll Area */
            QScrollArea#scrollArea {{
                border: 2px solid rgba(0, 245, 255, 0.3);
                border-radius: 15px;
                background: #000000;
                margin: 10px;
            }}
            
            QWidget#infoWidget {{
                background: #000000;
            }}
            
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.05);
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {Config.ACCENT_COLOR};
                border-radius: 6px;
                min-height: 30px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {Config.BUTTON_HOVER};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            
            /* Error Frame */
            QFrame#errorFrame {{
                background: #000000;
                border: 1px solid rgba(255, 23, 68, 0.3);
                border-radius: 15px;
                margin: 10px;
            }}
            
            /* Buttons */
            QPushButton#retryButton {{
                background: {Config.ACCENT_GRADIENT};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: {Config.FONT_SIZE_NORMAL}px;
                font-weight: bold;
            }}
            
            QPushButton#retryButton:hover {{
                background: {Config.BUTTON_HOVER};
            }}
            
            QPushButton#retryButton:pressed {{
                background: {Config.BUTTON_PRESSED};
            }}
            

            
            /* General Labels */
            QLabel {{
                color: {Config.TEXT_COLOR};
                font-family: '{Config.FONT_FAMILY}';
            }}
        """)
    
    def load_account_info(self):
        self.loading_frame.show()
        self.scroll_area.hide()
        self.error_frame.hide()
        self.worker = AccountInfoWorker()
        self.worker.finished.connect(self.on_account_info_loaded)
        self.worker.start()
    
    def on_account_info_loaded(self, success, data):
      
        self.loading_frame.hide()
        
        if success:
            self.account_data = data
            self.display_account_info()
            self.scroll_area.show()
        else:
            error_msg = data.get('error', 'Unknown error occurred')
            self.error_label.setText(f"Failed to load account information:\n{error_msg}")
            self.error_frame.show()
    
    def display_account_info(self):
      
        for i in reversed(range(self.info_layout.count())):
            self.info_layout.itemAt(i).widget().setParent(None)
        
        self.add_section_header("Basic Information")
        self.add_info_row("Username", self.account_data.get('username', 'N/A'))
        self.add_info_row("Email", self.account_data.get('email', 'N/A'))
        
        email_verified = self.account_data.get('email_verified', False)
        verification_text = "✅ Verified" if email_verified else "❌ Not Verified"
        self.add_info_row("Email Status", verification_text)
        
        self.add_section_header("Account Status")
        
        is_banned = self.account_data.get('is_banned', False)
        ban_reason = self.account_data.get('ban_reason', '')
        banned_at = self.account_data.get('banned_at', '')
        
        if is_banned:
            status_text = "🚫 BANNED"
            status_color = "#ff4444"
        else:
            status_text = "✅ Active"
            status_color = "#44ff44"
        
        status_label = self.add_info_row("Status", status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        
        if is_banned:
            if ban_reason:
                reason_label = self.add_info_row("Ban Reason", ban_reason)
                reason_label.setStyleSheet("color: #ff6666; font-weight: bold;")
            
            if banned_at:
                try:
                    ban_date = datetime.fromisoformat(banned_at.replace('Z', '+00:00'))
                    formatted_date = ban_date.strftime("%B %d, %Y at %I:%M %p")
                    ban_date_label = self.add_info_row("Banned On", formatted_date)
                    ban_date_label.setStyleSheet("color: #ff6666;")
                except:
                    self.add_info_row("Banned On", banned_at)
        
        self.add_section_header("Credits")
        
        try:
            from utils.session_manager import SessionManager
            session_manager = SessionManager()
            verified_credits = session_manager.get_credits_safely()
            credits = verified_credits
            credits_text = f"{credits} credits remaining (verified)"
        except Exception as e:
            credits = self.account_data.get('credits', 0)
            credits_text = f"{credits} credits remaining (unverified)"
            print(f"⚠️ Credit verification failed: {e}")
        
        credits_label = self.add_info_row("Available Credits", credits_text)
        
        if credits <= 0:
            credits_color = "#ff4444"
        elif credits <= 5:
            credits_color = "#ffaa44"
        else:
            credits_color = "#44ff44"
        
        credits_label.setStyleSheet(f"color: {credits_color}; font-weight: bold;")
        
        self.add_section_header("Account Dates")
        
        created_at = self.account_data.get('created_at', '')
        if created_at:
            try:
                reg_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                formatted_reg_date = reg_date.strftime("%B %d, %Y at %I:%M %p")
                self.add_info_row("Registered", formatted_reg_date)
            except:
                self.add_info_row("Registered", created_at)
        
        last_activity = self.account_data.get('last_activity', '')
        if last_activity:
            try:
                activity_date = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                formatted_activity = activity_date.strftime("%B %d, %Y at %I:%M %p")
                self.add_info_row("Last Activity", formatted_activity)
            except:
                self.add_info_row("Last Activity", last_activity)
        
        self.add_section_header("Technical Information")
        
        user_id = self.account_data.get('id', 'N/A')
        self.add_info_row("User ID", user_id)
        
        session_valid = self.account_data.get('session_valid', False)
        session_text = "✅ Valid" if session_valid else "❌ Invalid"
        self.add_info_row("Session", session_text)
    
    def add_section_header(self, title):
        header_frame = QFrame()
        header_frame.setObjectName("sectionHeader")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        icon_map = {
            "Basic Information": "👤",
            "Account Status": "🛡️",
            "Credits": "💰",
            "Account Dates": "📅",
            "Technical Information": "⚙️"
        }
        
        icon = QLabel(icon_map.get(title, "📋"))
        icon.setFont(QFont(Config.FONT_FAMILY, 16))
        header_layout.addWidget(icon)
        
        header = QLabel(title)
        header.setFont(QFont(Config.FONT_FAMILY, 16, QFont.Bold))
        header.setStyleSheet(f"""
            color: white;
            font-weight: bold;
            padding: 0px 10px;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        header_frame.setStyleSheet(f"""
            QFrame#sectionHeader {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0,245,255,0.8), 
                    stop:0.3 rgba(0,188,212,0.7), 
                    stop:0.7 rgba(138,43,226,0.6), 
                    stop:1 rgba(255,64,129,0.7));
                border-radius: 12px;
                margin: 15px 0px 10px 0px;
                border: 2px solid rgba(0, 245, 255, 0.4);
            }}
        """)
        
        self.info_layout.addWidget(header_frame)
    
    def add_info_row(self, label_text, value_text):
        row_frame = QFrame()
        row_frame.setObjectName("infoRow")
        
        value_str = str(value_text)
        use_vertical = len(value_str) > 25 or '@' in value_str or len(label_text) > 11
        
        if use_vertical:
            row_layout = QVBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 12, 15, 12)
            row_layout.setSpacing(8)
        else:
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 12, 15, 12)
            row_layout.setSpacing(15)
        
        label = QLabel(f"{label_text}:")
        label.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, QFont.Bold))
        
        if use_vertical:
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(f"""
                color: {Config.ACCENT_COLOR};
                font-weight: bold;
                margin-bottom: 5px;
            """)
        else:
            label.setMinimumWidth(160)
            label.setMaximumWidth(160)
            label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            label.setStyleSheet(f"""
                color: {Config.ACCENT_COLOR};
                font-weight: bold;
                padding-top: 8px;
            """)
        
        value = QLabel(str(value_text))
        value.setWordWrap(True)
        value.setFont(QFont(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        value.setMinimumHeight(35)
        value.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        value.setStyleSheet(f"""
            color: {Config.TEXT_COLOR};
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 rgba(0, 245, 255, 0.08), 
                stop:0.5 rgba(255, 255, 255, 0.03), 
                stop:1 rgba(138, 43, 226, 0.06));
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(0, 245, 255, 0.3);
            font-weight: 500;
        """)
        
        row_layout.addWidget(label)
        if use_vertical:
            row_layout.addWidget(value)
        else:
            row_layout.addWidget(value, 1)
        
        row_frame.setStyleSheet(f"""
            QFrame#infoRow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0, 188, 212, 0.12), 
                    stop:0.3 rgba(255, 255, 255, 0.05), 
                    stop:0.7 rgba(138, 43, 226, 0.08), 
                    stop:1 rgba(0, 245, 255, 0.1));
                border: 1px solid rgba(0, 245, 255, 0.25);
                border-radius: 15px;
                margin: 5px 0px;
            }}
            QFrame#infoRow:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgba(0, 188, 212, 0.2), 
                    stop:0.3 rgba(255, 255, 255, 0.1), 
                    stop:0.7 rgba(138, 43, 226, 0.15), 
                    stop:1 rgba(0, 245, 255, 0.18));
                border: 2px solid rgba(0, 245, 255, 0.5);
            }}
        """)
        
        self.info_layout.addWidget(row_frame)
        return value
    
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()