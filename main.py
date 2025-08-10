
import sys
import os
import warnings

warnings.filterwarnings("ignore", message=".*Qt::AA_EnableHighDpiScaling.*")

os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '1'

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from PyQt5.QtGui import QIcon, QFont

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.splash_screen import SplashScreen
from ui.auth_window import AuthWindow
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from utils.session_manager import SessionManager
from utils.config import Config

class BlackWormApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        
        self.db_manager = DatabaseManager()
        self.session_manager = SessionManager()
        
        self.splash_screen = None
        self.auth_window = None
        self.main_window = None
        
    def setup_application(self):
        self.app.setApplicationName("Black Worm")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Black Worm AI")
        
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
        
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
    
    def show_splash_screen(self):
        self.splash_screen = SplashScreen()
        self.splash_screen.finished.connect(self.on_splash_finished)
        self.splash_screen.show()
    
    def on_splash_finished(self):
        self.splash_screen.close()
        self.check_session_and_show_appropriate_window()
    
    def check_session_and_show_appropriate_window(self):
        try:
            if self.session_manager.has_valid_session():
                print("✅ Valid session found, validating with server...")
                
                is_valid, response = self.session_manager.validate_session_with_server()
                if is_valid:
                    print("✅ Server validation successful, loading main window")
                    self.show_main_window()
                else:
                    error_msg = response.get('error', 'Unknown error')
                    print(f"❌ Session validation failed: {error_msg}")
                    print("🔄 Redirecting to login window")
                    self.show_auth_window()
            else:
                print("ℹ️ No valid session found, showing authentication window")
                self.show_auth_window()
        except Exception as e:
            print(f"⚠️ Error checking session: {e}")
            try:
                self.session_manager.clear_session()
            except:
                pass
            print("🔄 Redirecting to login window due to error")
            self.show_auth_window()
    
    def show_auth_window(self):
        self.auth_window = AuthWindow()
        self.auth_window.login_successful.connect(self.on_login_successful)
        self.auth_window.show()
    
    def show_main_window(self):
        user_data = self.session_manager.get_user_data()
        self.main_window = MainWindow(user_data)
        self.main_window.logout_requested.connect(self.on_logout_requested)
        self.main_window.show()
        
        if self.auth_window:
            self.auth_window.close()
    
    def on_login_successful(self, user_data):
        self.session_manager.save_session(user_data)
        self.show_main_window()
    
    def on_logout_requested(self):
        self.session_manager.clear_session()
        if self.main_window:
            self.main_window.close()
        self.show_auth_window()
    
    def run(self):
        try:
            self.db_manager.initialize_database()
            
            self.show_splash_screen()
            
            return self.app.exec_()
            
        except Exception as e:
            print(f"Application error: {e}")
            return 1

def main():
    try:
        app = BlackWormApp()
        sys.exit(app.run())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()