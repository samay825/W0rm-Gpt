
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QWidget,
                             QApplication, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QDesktopServices
import sys
import os
import webbrowser
import requests
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.config import Config
from utils.api_client import APIClient

class CreditPlanWidget(QWidget):
    
    purchase_clicked = pyqtSignal(str, str, int)  # plan_name, price, credits
    
    def __init__(self, price, credits, remarks, is_best=False):
        super().__init__()
        self.price = price
        self.credits = credits
        self.remarks = remarks
        self.is_best = is_best
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        plan_container = QFrame()
        plan_container.setObjectName("planContainer")
        plan_container.setMinimumHeight(220)  # Ensure minimum height
        plan_container.setMaximumHeight(270)  # Set maximum height
        
        if self.is_best:
            plan_container.setStyleSheet(f"""
                QFrame#planContainer {{
                    background: {Config.ACCENT_GRADIENT};
                    border: 3px solid {Config.ACCENT_COLOR};
                    border-radius: 18px;
                    margin: 5px;
                }}
            """)
        else:
            plan_container.setStyleSheet(f"""
                QFrame#planContainer {{
                    background: {Config.CARD_GRADIENT};
                    border: 2px solid rgba(0, 245, 255, 0.3);
                    border-radius: 18px;
                    margin: 5px;
                }}
                QFrame#planContainer:hover {{
                    background: {Config.TEAL_GRADIENT};
                    border: 2px solid {Config.ACCENT_COLOR};
                }}
            """)
        
        plan_layout = QVBoxLayout(plan_container)
        plan_layout.setContentsMargins(15, 15, 15, 15)
        plan_layout.setSpacing(10)
        
        if self.is_best:
            best_badge = QLabel("🏆 BEST")
            best_badge.setAlignment(Qt.AlignCenter)
            best_badge.setStyleSheet(f"""
                QLabel {{
                    color: #1a1a1a;
                    font-size: {Config.FONT_SIZE_SMALL}px;
                    font-weight: 800;
                    font-family: '{Config.FONT_FAMILY}';
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 8px;
                    padding: 4px 8px;
                    margin-bottom: 5px;
                }}
            """)
            plan_layout.addWidget(best_badge)
        
        # Price
        price_label = QLabel(self.price)
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet(f"""
            QLabel {{
                color: {'#1a1a1a' if self.is_best else 'white'};
                font-size: {Config.FONT_SIZE_LARGE + 4}px;
                font-weight: 800;
                font-family: '{Config.FONT_FAMILY}';
                margin: 5px 0px;
            }}
        """)
        
        display_credits = self.credits // 100
        credits_label = QLabel(f"{display_credits:,} Credits")
        credits_label.setAlignment(Qt.AlignCenter)
        credits_label.setWordWrap(True)
        credits_label.setStyleSheet(f"""
            QLabel {{
                color: {'#1a1a1a' if self.is_best else Config.ACCENT_COLOR};
                font-size: {Config.FONT_SIZE_MEDIUM}px;
                font-weight: 700;
                font-family: '{Config.FONT_FAMILY}';
                margin: 3px 0px;
            }}
        """)
        
        remarks_label = QLabel(self.remarks)
        remarks_label.setAlignment(Qt.AlignCenter)
        remarks_label.setWordWrap(True)
        remarks_label.setStyleSheet(f"""
            QLabel {{
                color: {'#333333' if self.is_best else Config.TEXT_SECONDARY};
                font-size: {Config.FONT_SIZE_NORMAL}px;
                font-weight: 600;
                font-family: '{Config.FONT_FAMILY}';
                margin: 3px 0px 8px 0px;
            }}
        """)
        
        buy_button = QPushButton("💳 Buy Now")
        buy_button.setObjectName("buyButton")
        buy_button.setMinimumHeight(50)
        buy_button.setMinimumWidth(140)
        buy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        buy_button.clicked.connect(self.on_buy_clicked)
        
        if self.is_best:
            buy_button.setStyleSheet(f"""
                QPushButton#buyButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #1a1a1a, stop:1 #333333);
                    border: 2px solid rgba(255, 255, 255, 0.8);
                    border-radius: 12px;
                    padding: 12px 20px;
                    color: white;
                    font-size: {Config.FONT_SIZE_MEDIUM}px;
                    font-weight: 800;
                    font-family: '{Config.FONT_FAMILY}';
                    text-align: center;
                }}
                QPushButton#buyButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #333333, stop:1 #555555);
                    border: 2px solid #ffffff;
                }}
                QPushButton#buyButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #555555, stop:1 #777777);
                    border: 2px solid #cccccc;
                }}
            """)
        else:
            buy_button.setStyleSheet(f"""
                QPushButton#buyButton {{
                    background: {Config.ACCENT_GRADIENT};
                    border: 2px solid {Config.ACCENT_COLOR};
                    border-radius: 12px;
                    padding: 12px 20px;
                    color: #1a1a1a;
                    font-size: {Config.FONT_SIZE_MEDIUM}px;
                    font-weight: 800;
                    font-family: '{Config.FONT_FAMILY}';
                    text-align: center;
                }}
                QPushButton#buyButton:hover {{
                    background: {Config.NEON_GRADIENT};
                    border: 2px solid #00ffff;
                    color: #1a1a1a;
                }}
                QPushButton#buyButton:pressed {{
                    background: {Config.TEAL_GRADIENT};
                    border: 2px solid #00bcd4;
                    color: #1a1a1a;
                }}
            """)
        
        plan_layout.addWidget(price_label)
        plan_layout.addWidget(credits_label)
        plan_layout.addWidget(remarks_label)
        plan_layout.addWidget(buy_button)
        
        layout.addWidget(plan_container)
        self.setLayout(layout)
    
    def on_buy_clicked(self):
        plan_name = getattr(self, 'package_name', f"{self.price} Plan")
        self.purchase_clicked.emit(plan_name, self.price, self.credits)

class CreditPurchaseDialog(QDialog):

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.seller_username = "@sands123" 
        self.api_client = APIClient()
        self.fetch_seller_username()
        self.setup_window()
        self.setup_ui()
    
    def fetch_seller_username(self):
        try:
            success, response_data = self.api_client.get_public_settings()
            if success and 'data' in response_data and 'settings' in response_data['data']:
                settings = response_data['data']['settings']
                if 'sellerUsername' in settings:
                    self.seller_username = settings['sellerUsername']
                    print(f"Fetched seller username: {self.seller_username}")
                else:
                    print("Seller username not found in settings, using default")
            else:
                print("Failed to fetch settings, using default seller username")
        except Exception as e:
            print(f"Error fetching seller username: {e}")

    def setup_window(self):
        self.setWindowTitle("💳 Buy Credits - Black Worm")
        self.setFixedSize(1000, 750)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen = QApplication.desktop().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_container = QFrame()
        main_container.setObjectName("mainContainer")
        main_container.setStyleSheet(f"""
            QFrame#mainContainer {{
                background: {Config.MODERN_GRADIENT_1};
                border: 2px solid {Config.ACCENT_COLOR};
                border-radius: 20px;
            }}
        """)
        
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(25, 25, 25, 25)
        container_layout.setSpacing(20)
        
        self.create_title_bar(container_layout)
        
        self.create_header_section(container_layout)
        
        self.create_plans_section(container_layout)
        
        self.create_footer_section(container_layout)
        
        main_layout.addWidget(main_container)
        self.setLayout(main_layout)
    
    def create_title_bar(self, layout):
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("💎 Buy Credits")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.FONT_SIZE_HEADER}px;
                font-weight: 900;
                font-family: '{Config.FONT_FAMILY}';
                background: transparent;
            }}
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(40, 40)
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton#closeButton {{
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }}
            QPushButton#closeButton:hover {{
                background: {Config.ERROR_COLOR};
            }}
            QPushButton#closeButton:pressed {{
                background: #cc1234;
            }}
        """)
        
        title_layout.addWidget(close_btn)
        layout.addWidget(title_bar)
    
    def create_header_section(self, layout):
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        
        welcome_label = QLabel(f"Welcome, {self.user_data.get('username', 'User')}!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {Config.FONT_SIZE_TITLE}px;
                font-weight: 800;
                font-family: '{Config.FONT_FAMILY}';
                margin: 15px 0px 25px 0px;
            }}
        """)
        
        header_layout.addWidget(welcome_label)
        layout.addWidget(header_frame)
    
    def create_plans_section(self, layout):
        plans_frame = QFrame()
        plans_layout = QVBoxLayout(plans_frame)
        plans_layout.setContentsMargins(0, 0, 0, 0)
        plans_layout.setSpacing(20)
        
        plans_title = QLabel("🚀 Choose Your Plan")
        plans_title.setAlignment(Qt.AlignCenter)
        plans_title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {Config.FONT_SIZE_TITLE}px;
                font-weight: 800;
                font-family: '{Config.FONT_FAMILY}';
                margin: 15px 0px 25px 0px;
            }}
        """)
        plans_layout.addWidget(plans_title)
        
        plans_container = QWidget()
        plans_grid = QHBoxLayout(plans_container)
        plans_grid.setContentsMargins(10, 0, 10, 0)
        plans_grid.setSpacing(20)
        
        plans_data = self.fetch_credit_packages()
        
        for plan_data in plans_data:
            plan_widget = CreditPlanWidget(
                plan_data["price"],
                plan_data["credits"],
                plan_data["remarks"],
                plan_data.get("is_best", False)
            )
            plan_widget.package_name = plan_data.get("package_name", f"{plan_data['price']} Plan")
            plan_widget.setMinimumWidth(200)
            plan_widget.setMaximumWidth(220)
            plan_widget.purchase_clicked.connect(self.handle_purchase)
            plans_grid.addWidget(plan_widget)
        
        plans_layout.addWidget(plans_container)
        layout.addWidget(plans_frame)
    
    def create_footer_section(self, layout):
        footer_frame = QFrame()
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(10)
        
        info_label = QLabel(f"🔥 After clicking 'Buy Now', you'll be redirected to Telegram ({self.seller_username}) to complete your purchase!")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.ACCENT_COLOR};
                font-size: {Config.FONT_SIZE_MEDIUM}px;
                font-weight: 600;
                font-family: '{Config.FONT_FAMILY}';
                margin: 15px 0px;
                padding: 20px;
                background: {Config.CARD_GRADIENT};
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 15px;
            }}
        """)
        
        footer_layout.addWidget(info_label)
        layout.addWidget(footer_frame)
    
    def fetch_credit_packages(self):
        try:
            response = requests.get(f"{Config.API_BASE_URL}/credit-packages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data', {}).get('packages'):
                    packages = data['data']['packages']
                    
                    plans_data = []
                    for package in packages:
                        plans_data.append({
                            "price": f"${package['price']:.0f}",
                            "credits": package['credits'],
                            "remarks": package.get('description', ''),
                            "is_best": package.get('is_best_value', False),
                            "package_id": package['id'],
                            "package_name": package['name']
                        })
                    
                    print(f"✅ Fetched {len(plans_data)} credit packages from backend")
                    return plans_data
                else:
                    print("⚠️ No packages found in backend response")
            else:
                print(f"⚠️ Backend request failed with status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Failed to fetch credit packages from backend: {e}")
        except Exception as e:
            print(f"⚠️ Error processing credit packages: {e}")
        
        print("🔄 Using fallback credit packages")
        return [
            {"price": "$10", "credits": 10000, "remarks": "Basic Plan", "is_best": False},
            {"price": "$25", "credits": 27500, "remarks": "Popular Plan - 10% bonus", "is_best": False},
            {"price": "$50", "credits": 60000, "remarks": "Value Plan - 20% bonus", "is_best": False},
            {"price": "$100", "credits": 130000, "remarks": "Premium Plan - 30% bonus", "is_best": True}
        ]
    
    def handle_purchase(self, plan_name, price, credits):
        try:
            username = self.user_data.get('username', 'Unknown')
            
            message = f"Hey, I want to Buy Credit ({plan_name}) and My username is ({username})."
            
            import urllib.parse
            encoded_message = urllib.parse.quote(message)
            
            telegram_username = self.seller_username.lstrip('@')
            telegram_url = f"https://t.me/{telegram_username}?text={encoded_message}"
            
            
            print(f"🔄 Opening Telegram for purchase: {plan_name}")
            print(f"📱 Message: {message}")
            
            success = QDesktopServices.openUrl(QUrl(telegram_url))
            
            if success:
                print("✅ Telegram opened successfully")
                self.accept()
            else:
                print("❌ Failed to open Telegram, trying browser fallback")
                webbrowser.open(telegram_url)
                self.accept()
                
        except Exception as e:
            print(f"❌ Error opening Telegram: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to open Telegram. Please contact support manually.\n\nPlan: {plan_name}\nUsername: {username}"
            )
    
    def paintEvent(self, event):
        super().paintEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    test_user_data = {
        'username': 'TestUser',
        'credits': 1500
    }
    
    dialog = CreditPurchaseDialog(test_user_data)
    dialog.show()
    
    sys.exit(app.exec_())