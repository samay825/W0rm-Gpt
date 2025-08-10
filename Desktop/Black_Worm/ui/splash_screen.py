from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPixmap, QLinearGradient, QBrush, QPen
from utils.config import Config

class SplashScreen(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(900, 700)

        screen = QApplication.desktop().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(40)
        layout.setContentsMargins(60, 80, 60, 80)
        
        self.title_label = QLabel("🐛 Black Worm")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-family: '{Config.FONT_FAMILY}';
                font-size: {Config.FONT_SIZE_HEADER + 32}px;
                font-weight: 800;
                background: transparent;
                margin: 20px 0px;
            }}
        """)
        
        self.subtitle_label = QLabel("✨ The Ultra-Modern AI Agent ✨")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.TEXT_SECONDARY};
                font-family: '{Config.FONT_FAMILY}';
                font-size: {Config.FONT_SIZE_LARGE + 8}px;
                font-weight: 600;
                background: transparent;
                margin: 10px 0px;
            }}
        """)
        
        # Loading indicator
        self.loading_label = QLabel("🚀 Initializing Ultra-Modern Interface...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.TEXT_COLOR};
                font-family: '{Config.FONT_FAMILY}';
                font-size: {Config.FONT_SIZE_MEDIUM + 2}px;
                font-weight: 600;
                background: transparent;
                margin-top: 60px;
            }}
        """)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.loading_label)
        
        self.setLayout(layout)
        
        self.setStyleSheet("background: transparent;")
    
    def setup_animation(self):
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1500) 
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.glitch_timer = QTimer()
        self.glitch_timer.timeout.connect(self.glitch_effect)
        self.glitch_timer.start(300) 

        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.loading_timer.start(500)
        self.loading_dots = 0

        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.fade_out)
        self.close_timer.setSingleShot(True)
        self.close_timer.start(Config.SPLASH_DURATION + 1000)  # Show longer
        self.fade_animation.start()
    
    def animate_loading(self):
        dots = "." * (self.loading_dots % 4)
        self.loading_label.setText(f"🚀 Initializing Ultra-Modern Interface{dots}")
        self.loading_dots += 1
    
    def glitch_effect(self):
        import random
        glitch_chars = ['█', '▓', '▒', '░', '▄', '▀', '■', '□']

        if random.random() < 0.3:  
            original_text = "🐛 Black Worm"
            glitched_text = ""
            
            for char in original_text:
                if char in ['🐛', ' ']: 
                    glitched_text += char
                elif random.random() < 0.2: 
                    glitched_text += random.choice(glitch_chars)
                else:
                    glitched_text += char
            
            self.title_label.setText(glitched_text)
            
            QTimer.singleShot(100, lambda: self.title_label.setText("🐛 Black Worm"))
    
    def fade_out(self):

        self.glitch_timer.stop()
        self.loading_timer.stop()
        

        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(800)  # Slower fade out
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.finished.emit)
        self.fade_out_animation.start()
    
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
        pen = QPen(QColor(Config.ACCENT_COLOR), 4)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 35, 35)
        inner_pen = QPen(QColor(Config.ACCENT_COLOR))
        inner_pen.setWidth(1)
        painter.setPen(inner_pen)
        painter.drawRoundedRect(self.rect().adjusted(6, 6, -6, -6), 30, 30)