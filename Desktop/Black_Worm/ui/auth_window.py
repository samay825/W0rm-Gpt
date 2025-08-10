
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QStackedWidget, QFrame,
                            QMessageBox, QProgressBar, QCheckBox, QGraphicsDropShadowEffect,
                            QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QPropertyAnimation, QEasingCurve, QEventLoop
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPainter, QLinearGradient, QBrush, QColor, QPen, QFontMetrics
from utils.config import Config
from utils.api_client import APIClient
import re

class AuthWorker(QThread):
    finished = pyqtSignal(bool, dict)
    
    def __init__(self, action, **kwargs):
        super().__init__()
        self.action = action
        self.kwargs = kwargs
        self.api_client = APIClient()
    
    def run(self):
        try:
            if self.action == 'register':
                success, data = self.api_client.register(
                    self.kwargs['email'],
                    self.kwargs['username'],
                    self.kwargs['password']
                )
            elif self.action == 'login':
                success, data = self.api_client.login(
                    self.kwargs['email'],
                    self.kwargs['password']
                )
            elif self.action == 'verify_otp':
                success, data = self.api_client.verify_otp(
                    self.kwargs['email'],
                    self.kwargs['otp']
                )
            elif self.action == 'resend_otp':
                success, data = self.api_client.resend_otp(
                    self.kwargs['email']
                )
            else:
                success, data = False, {'error': 'Unknown action'}
            
            self.finished.emit(success, data)
        except Exception as e:
            self.finished.emit(False, {'error': str(e)})

class ModernInputField(QLineEdit):
    
    def __init__(self, placeholder="", is_password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.Password)
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px 18px;
                font-size: 15px;
                color: {Config.TEXT_COLOR};
                font-weight: 500;
                font-family: '{Config.FONT_FAMILY}';
                selection-background-color: {Config.ACCENT_COLOR};
                line-height: 1.4;
                min-height: 20px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {Config.ACCENT_COLOR};
                background: rgba(255, 255, 255, 0.12);
                outline: none;
            }}
            
            QLineEdit:hover {{
                border: 2px solid rgba(0, 245, 255, 0.5);
                background: rgba(255, 255, 255, 0.1);
            }}
        """)

class ModernButton(QPushButton):
    
    def __init__(self, text, button_type="primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        if self.button_type == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Config.ACCENT_GRADIENT};
                    border: none;
                    border-radius: 12px;
                    padding: 14px 28px;
                    font-size: 16px;
                    font-weight: 700;
                    color: white;
                    font-family: '{Config.FONT_FAMILY}';
                    min-height: 18px;
                }}
                
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #00ffff, stop:1 #00ccff);
                }}
                
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #00ccff, stop:1 #0099ff);
                }}
                
                QPushButton:disabled {{
                    background: rgba(255, 255, 255, 0.1);
                    color: {Config.TEXT_MUTED};
                }}
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255, 255, 255, 0.08);
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 14px 28px;
                    font-size: 16px;
                    font-weight: 600;
                    color: {Config.TEXT_COLOR};
                    font-family: '{Config.FONT_FAMILY}';
                    min-height: 18px;
                }}
                
                QPushButton:hover {{
                    background: {Config.ACCENT_GRADIENT};
                    color: white;
                    border-color: {Config.ACCENT_COLOR};
                }}
                
                QPushButton:pressed {{
                    background: rgba(0, 245, 255, 0.8);
                }}
            """)
        elif self.button_type == "link":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {Config.ACCENT_COLOR};
                    font-size: 14px;
                    font-weight: 600;
                    font-family: '{Config.FONT_FAMILY}';
                    text-decoration: none;
                    padding: 8px 16px;
                }}
                
                QPushButton:hover {{
                    color: #00ffff;
                    text-decoration: underline;
                }}
                
                QPushButton:pressed {{
                    color: #00ccff;
                }}
            """)

class CustomMessageBox(QWidget):
    
    def __init__(self, parent, message, is_error=True):
        super().__init__(parent)
        self.message = message
        self.is_error = is_error
        self.result = None
        self.setup_ui()
        self.center_on_parent()
        
    def setup_ui(self):
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        container = QWidget()
        container.setObjectName("messageContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(20)
        
        message_label = QLabel(self.message)
        message_label.setObjectName("messageLabel")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        
        font = message_label.font()
        font.setPointSize(16)
        font.setFamily(Config.FONT_FAMILY)
        message_label.setFont(font)
        
        font_metrics = QFontMetrics(font)
        
        max_width = 400  # Maximum width for the message
        text_rect = font_metrics.boundingRect(0, 0, max_width - 50, 0, 
                                            Qt.TextWordWrap | Qt.AlignCenter, 
                                            self.message)
        
        text_width = min(max_width, text_rect.width() + 50)
        text_height = text_rect.height()
        
        min_width = 300
        min_height = 150
        max_height = 400
        
        dialog_width = max(min_width, text_width + 50)
        dialog_height = max(min_height, text_height + 120)  # Extra space for button and padding
        dialog_height = min(max_height, dialog_height)
        
        self.setFixedSize(dialog_width, dialog_height)
        
        ok_button = QPushButton("OK")
        ok_button.setObjectName("okButton")
        ok_button.setFixedSize(100, 40)
        ok_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        container_layout.addWidget(message_label)
        container_layout.addStretch()
        container_layout.addLayout(button_layout)
        
        layout.addWidget(container)
        
        self.setStyleSheet(f"""
            #messageContainer {{
                background: {Config.MODERN_GRADIENT_1};
                border: 2px solid {Config.ACCENT_COLOR};
                border-radius: 15px;
            }}
            
            #messageLabel {{
                color: {Config.TEXT_COLOR};
                font-family: '{Config.FONT_FAMILY}';
                font-size: 16px;
                font-weight: 500;
                background: transparent;
                padding: 15px;
                line-height: 1.5;
                margin: 0px;
                qproperty-alignment: AlignCenter;
            }}
            
            #okButton {{
                background: {Config.ACCENT_GRADIENT};
                border: none;
                border-radius: 10px;
                color: white;
                font-family: '{Config.FONT_FAMILY}';
                font-size: 14px;
                font-weight: 600;
            }}
            
            #okButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00ffff, stop:1 #00ccff);
            }}
            
            #okButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #00ccff, stop:1 #0099ff);
            }}
        """)
    
    def center_on_parent(self):
        if self.parent():
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            x = parent_center.x() - self.width() // 2
            y = parent_center.y() - self.height() // 2
            
            screen = QApplication.primaryScreen().geometry()
            x = max(screen.x(), min(x, screen.x() + screen.width() - self.width()))
            y = max(screen.y(), min(y, screen.y() + screen.height() - self.height()))
            
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
    
    def accept(self):
        self.result = True
        self.close()
    
    def exec_(self):
        self.show()
        self.raise_()
        self.activateWindow()
        
        loop = QEventLoop()
        self.destroyed.connect(loop.quit)
        loop.exec_()
        
        return self.result

class AuthWindow(QWidget):
    login_successful = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_email = ""
        self.drag_position = None
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        self.setWindowTitle("Black Worm - Authentication")
        self.setFixedSize(520, 800)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        screen = self.screen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.create_title_bar(main_layout)
        
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(35, 20, 35, 35)
        content_layout.setSpacing(15)
        
        self.create_header(content_layout)
        
        self.stacked_widget = QStackedWidget()
        
        self.login_screen = self.create_login_screen()
        self.register_screen = self.create_register_screen()
        self.otp_screen = self.create_otp_screen()
        
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.register_screen)
        self.stacked_widget.addWidget(self.otp_screen)
        
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)
        
        self.setup_styles()
        
    def create_title_bar(self, main_layout):
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setObjectName("titleBar")
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Authentication")
        title.setObjectName("titleBarText")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(35, 35)
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)
        
    def create_header(self, layout):
        title_label = QLabel("🐛 Black Worm")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("Ultra-Modern AI Agent")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("subtitleLabel")
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(10)
        
    def create_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        welcome_label = QLabel("Welcome Back")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("welcomeLabel")
        
        self.login_email = ModernInputField("Enter your email address")
        
        self.login_password = ModernInputField("Enter your password", is_password=True)
        self.login_password.returnPressed.connect(self.handle_login)
        
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setObjectName("checkBox")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        forgot_link = ModernButton("Forgot Password?", "link")
        remember_layout.addWidget(forgot_link)
        
        login_btn = ModernButton("Sign In", "primary")
        login_btn.clicked.connect(self.handle_login)
        
        self.login_progress = QProgressBar()
        self.login_progress.setVisible(False)
        self.login_progress.setObjectName("progressBar")
        
        divider_layout = QHBoxLayout()
        divider_line1 = QFrame()
        divider_line1.setFrameShape(QFrame.HLine)
        divider_line1.setObjectName("dividerLine")
        
        divider_text = QLabel("or")
        divider_text.setObjectName("dividerText")
        divider_text.setAlignment(Qt.AlignCenter)
        
        divider_line2 = QFrame()
        divider_line2.setFrameShape(QFrame.HLine)
        divider_line2.setObjectName("dividerLine")
        
        divider_layout.addWidget(divider_line1)
        divider_layout.addWidget(divider_text)
        divider_layout.addWidget(divider_line2)
        
        register_link = ModernButton("Create New Account", "secondary")
        register_link.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.register_screen))
        
        layout.addWidget(welcome_label)
        layout.addSpacing(8)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_password)
        layout.addLayout(remember_layout)
        layout.addWidget(login_btn)
        layout.addWidget(self.login_progress)
        layout.addSpacing(15)
        layout.addLayout(divider_layout)
        layout.addSpacing(8)
        layout.addWidget(register_link)
        layout.addStretch()
        
        return widget
        
    def create_register_screen(self):
        """Create professional registration screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        welcome_label = QLabel("Create Account")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setObjectName("welcomeLabel")
        
        self.register_email = ModernInputField("Email address")
        self.register_username = ModernInputField("Username")
        self.register_password = ModernInputField("Password", is_password=True)
        self.register_confirm_password = ModernInputField("Confirm password", is_password=True)
        self.register_confirm_password.returnPressed.connect(self.handle_register)
        
        terms_layout = QHBoxLayout()
        self.terms_checkbox = QCheckBox("I agree to the Terms of Service and Privacy Policy")
        self.terms_checkbox.setObjectName("checkBox")
        terms_layout.addWidget(self.terms_checkbox)
        
        register_btn = ModernButton("Create Account", "primary")
        register_btn.clicked.connect(self.handle_register)
        
        self.register_progress = QProgressBar()
        self.register_progress.setVisible(False)
        self.register_progress.setObjectName("progressBar")
        
        divider_layout = QHBoxLayout()
        divider_line1 = QFrame()
        divider_line1.setFrameShape(QFrame.HLine)
        divider_line1.setObjectName("dividerLine")
        
        divider_text = QLabel("or")
        divider_text.setObjectName("dividerText")
        divider_text.setAlignment(Qt.AlignCenter)
        
        divider_line2 = QFrame()
        divider_line2.setFrameShape(QFrame.HLine)
        divider_line2.setObjectName("dividerLine")
        
        divider_layout.addWidget(divider_line1)
        divider_layout.addWidget(divider_text)
        divider_layout.addWidget(divider_line2)
        
        login_link = ModernButton("Already have an account? Sign In", "secondary")
        login_link.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_screen))
        
        layout.addWidget(welcome_label)
        layout.addSpacing(6)
        layout.addWidget(self.register_email)
        layout.addWidget(self.register_username)
        layout.addWidget(self.register_password)
        layout.addWidget(self.register_confirm_password)
        layout.addSpacing(5)
        layout.addLayout(terms_layout)
        layout.addSpacing(5)
        layout.addWidget(register_btn)
        layout.addWidget(self.register_progress)
        layout.addSpacing(12)
        layout.addLayout(divider_layout)
        layout.addSpacing(6)
        layout.addWidget(login_link)
        layout.addStretch()
        
        return widget
        
    def create_otp_screen(self):
        """Create professional OTP verification screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(25)
        
        header_label = QLabel("Verify Your Email")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setObjectName("welcomeLabel")
        
        self.otp_info_label = QLabel("We've sent a 6-digit verification code to your email address")
        self.otp_info_label.setAlignment(Qt.AlignCenter)
        self.otp_info_label.setObjectName("infoLabel")
        self.otp_info_label.setWordWrap(True)
        
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter 6-digit code")
        self.otp_input.setMaxLength(6)
        self.otp_input.setAlignment(Qt.AlignCenter)
        self.otp_input.setObjectName("otpField")
        self.otp_input.returnPressed.connect(self.handle_verify_otp)
        
        verify_btn = ModernButton("Verify Code", "primary")
        verify_btn.clicked.connect(self.handle_verify_otp)
        
        self.otp_progress = QProgressBar()
        self.otp_progress.setVisible(False)
        self.otp_progress.setObjectName("progressBar")
        
        resend_layout = QHBoxLayout()
        resend_text = QLabel("Didn't receive the code?")
        resend_text.setObjectName("infoLabel")
        
        self.resend_btn = ModernButton("Resend Code", "link")
        self.resend_btn.clicked.connect(self.handle_resend_otp)
        
        resend_layout.addStretch()
        resend_layout.addWidget(resend_text)
        resend_layout.addWidget(self.resend_btn)
        resend_layout.addStretch()
        
        back_btn = ModernButton("Back to Login", "secondary")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_screen))
        
        layout.addWidget(header_label)
        layout.addWidget(self.otp_info_label)
        layout.addSpacing(20)
        layout.addWidget(self.otp_input)
        layout.addWidget(verify_btn)
        layout.addWidget(self.otp_progress)
        layout.addSpacing(30)
        layout.addLayout(resend_layout)
        layout.addSpacing(20)
        layout.addWidget(back_btn)
        layout.addStretch()
        
        return widget
        
    def setup_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                color: {Config.TEXT_COLOR};
                font-family: '{Config.FONT_FAMILY}';
                font-size: {Config.FONT_SIZE_NORMAL}px;
            }}
            
            #titleBar {{
                background: rgba(255, 255, 255, 0.05);
                border-bottom: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 20px 20px 0px 0px;
            }}
            
            #titleBarText {{
                color: {Config.ACCENT_COLOR};
                font-size: 16px;
                font-weight: 700;
                font-family: '{Config.FONT_FAMILY}';
            }}
            
            #closeButton {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {Config.TEXT_COLOR};
                font-size: 22px;
                font-weight: bold;
                border-radius: 17px;
            }}
            
            #closeButton:hover {{
                background-color: {Config.ERROR_COLOR};
                border-color: {Config.ERROR_COLOR};
                color: white;
            }}
            
            #titleLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: 38px;
                font-weight: 800;
                margin: 8px 0;
                font-family: '{Config.FONT_FAMILY}';
            }}
            
            #subtitleLabel {{
                color: {Config.TEXT_SECONDARY};
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
                font-family: '{Config.FONT_FAMILY}';
            }}
            
            #welcomeLabel {{
                color: {Config.TEXT_COLOR};
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 8px;
                font-family: '{Config.FONT_FAMILY}';
            }}
            
            #infoLabel {{
                color: {Config.TEXT_SECONDARY};
                font-size: 15px;
                font-weight: 500;
                line-height: 1.6;
                font-family: '{Config.FONT_FAMILY}';
            }}
            
            #otpField {{
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(0, 245, 255, 0.3);
                border-radius: 16px;
                padding: 22px 20px;
                font-size: 28px;
                font-weight: 800;
                color: {Config.ACCENT_COLOR};
                font-family: '{Config.FONT_FAMILY_MONO}';
                letter-spacing: 8px;
                line-height: 1.2;
                min-height: 32px;
            }}
            
            #otpField:focus {{
                border: 2px solid {Config.ACCENT_COLOR};
                background: rgba(255, 255, 255, 0.12);
                outline: none;
            }}
            
            #checkBox {{
                color: {Config.TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
                spacing: 8px;
            }}
            
            #checkBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background: rgba(255, 255, 255, 0.08);
            }}
            
            #checkBox::indicator:checked {{
                background: {Config.ACCENT_COLOR};
                border-color: {Config.ACCENT_COLOR};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            
            #dividerLine {{
                border: none;
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 0 10px;
            }}
            
            #dividerText {{
                color: {Config.TEXT_MUTED};
                font-size: 14px;
                font-weight: 500;
                padding: 0 15px;
            }}
            
            #progressBar {{
                border: none;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.08);
                text-align: center;
                height: 8px;
            }}
            
            #progressBar::chunk {{
                background: {Config.ACCENT_GRADIENT};
                border-radius: 8px;
            }}
        """)
        
    def setup_animations(self):
        self.setWindowOpacity(0.0)
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(800)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#0a0a0a"))
        gradient.setColorAt(0.3, QColor("#1a1a1a"))
        gradient.setColorAt(0.7, QColor("#2d2d2d"))
        gradient.setColorAt(1, QColor("#0a0a0a"))
        
        painter.fillRect(self.rect(), QBrush(gradient))
        
        pen = QPen(QColor(Config.ACCENT_COLOR), 3)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 20, 20)
        
        inner_pen = QPen(QColor(Config.ACCENT_COLOR))
        inner_pen.setWidth(1)
        painter.setPen(inner_pen)
        painter.drawRoundedRect(self.rect().adjusted(4, 4, -4, -4), 17, 17)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    # Validation methods
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def show_message(self, title, message, is_error=True):
        dialog = CustomMessageBox(self, message, is_error)
        dialog.exec_()
    
    
    # Event handlers
    def handle_login(self):
        email = self.login_email.text().strip()
        password = self.login_password.text()
        
        if not email or not password:
            self.show_message("Error", "Please fill in all fields")
            return
        
        if not self.validate_email(email):
            self.show_message("Error", "Please enter a valid email address")
            return
        
        self.login_progress.setVisible(True)
        self.login_progress.setRange(0, 0)  # Indeterminate progress
        
        self.login_worker = AuthWorker('login', email=email, password=password)
        self.login_worker.finished.connect(self.on_login_finished)
        self.login_worker.start()
    
    def on_login_finished(self, success, data):
        self.login_progress.setVisible(False)
        
        if success:
            if data.get('token'):
                self.login_successful.emit(data)
            else:
                self.show_message("Login Failed", "Unexpected response from server")
        else:
            error_msg = data.get('error', 'Login failed')
            
            if 'verify your email' in error_msg.lower():
                self.show_message("Email Verification Required", error_msg)
            else:
                self.show_message("Login Failed", error_msg)
    
    def handle_register(self):
        email = self.register_email.text().strip()
        username = self.register_username.text().strip()
        password = self.register_password.text()
        confirm_password = self.register_confirm_password.text()
        
        if not all([email, username, password, confirm_password]):
            self.show_message("Error", "Please fill in all fields")
            return
        
        if not self.validate_email(email):
            self.show_message("Error", "Please enter a valid email address")
            return
        
        if password != confirm_password:
            self.show_message("Error", "Passwords do not match")
            return
        
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            self.show_message("Error", msg)
            return
        
        if not self.terms_checkbox.isChecked():
            self.show_message("Error", "Please accept the Terms of Service")
            return
        
        self.register_progress.setVisible(True)
        self.register_progress.setRange(0, 0)
        
        self.register_worker = AuthWorker('register', email=email, username=username, password=password)
        self.register_worker.finished.connect(self.on_register_finished)
        self.register_worker.start()
    
    def on_register_finished(self, success, data):
        self.register_progress.setVisible(False)
        
        if success:
            self.current_email = self.register_email.text().strip()
            
            requires_verification = data.get('requiresVerification', True)
            
            if not requires_verification:
                token = data.get('token')
                if token:
                    from utils.session_manager import SessionManager
                    session_manager = SessionManager()
                    
                    session_data = {
                        'token': token,
                        'email': data.get('email', self.current_email),
                        'username': data.get('username', ''),
                        'credits': data.get('credits', 0),
                        'emailVerified': True
                    }
                    session_manager.save_session(session_data)
                    
                    self.show_message("Registration Successful", 
                                    "Your account has been created successfully! You are now logged in.", 
                                    is_error=False)
                    
                    self.login_successful.emit(session_data)
                else:
                    self.show_message("Registration Error", "Registration successful but login failed. Please try logging in manually.")
            else:
                self.otp_info_label.setText(f"We've sent a verification code to {self.current_email}")
                self.stacked_widget.setCurrentWidget(self.otp_screen)
        else:
            error_msg = data.get('error', 'Registration failed')
            self.show_message("Registration Failed", error_msg)
    
    def handle_verify_otp(self):
        otp = self.otp_input.text().strip()
        
        if not otp or len(otp) != 6:
            self.show_message("Error", "Please enter a valid 6-digit code")
            return
        
        self.otp_progress.setVisible(True)
        self.otp_progress.setRange(0, 0)
        
        self.otp_worker = AuthWorker('verify_otp', email=self.current_email, otp=otp)
        self.otp_worker.finished.connect(self.on_otp_finished)
        self.otp_worker.start()
    
    def on_otp_finished(self, success, data):
        self.otp_progress.setVisible(False)
        
        if success:
            self.login_successful.emit(data)
        else:
            error_msg = data.get('error', 'Verification failed')
            self.show_message("Verification Failed", error_msg)
    
    def handle_resend_otp(self):
        if not self.current_email:
            self.show_message("Error", "No email address found")
            return
        
        self.resend_btn.setEnabled(False)
        self.resend_btn.setText("Sending...")
        
        self.resend_worker = AuthWorker('resend_otp', email=self.current_email)
        self.resend_worker.finished.connect(self.on_resend_finished)
        self.resend_worker.start()
    
    def on_resend_finished(self, success, data):
        QTimer.singleShot(30000, lambda: (
            self.resend_btn.setEnabled(True),
            self.resend_btn.setText("Resend Code")
        ))
        
        if success:
            self.show_message("Code Sent", f"A new verification code has been sent to {self.current_email}", False)
        else:
            error_msg = data.get('error', 'Failed to resend code')
            self.show_message("Resend Failed", error_msg)
            self.resend_btn.setEnabled(True)
            self.resend_btn.setText("Resend Code")