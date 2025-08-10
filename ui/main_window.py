
from PyQt5 .QtWidgets import (QMainWindow ,QWidget ,QVBoxLayout ,QHBoxLayout ,
QFrame ,QScrollArea ,QLineEdit ,QPushButton ,QLabel ,
QListWidget ,QSplitter ,QListWidgetItem ,QMenu ,
QApplication ,QGraphicsDropShadowEffect ,QSizePolicy ,
QMessageBox )
from PyQt5 .QtCore import Qt ,QThread ,pyqtSignal ,QTimer ,QPropertyAnimation ,QEasingCurve
from PyQt5 .QtGui import QFont ,QColor ,QPainter ,QLinearGradient ,QBrush ,QPen
from datetime import datetime
import sys
import os
import requests
import json


sys .path .append (os .path .dirname (os .path .dirname (__file__ )))
from utils .config import Config
from database .db_manager import DatabaseManager
from utils .session_manager import SessionManager
from utils .text_formatter import TextFormatter
from ui .credit_purchase_dialog import CreditPurchaseDialog
from ui .chat_item_widget import ChatItemWidget
from ui .code_block_widget import EnhancedMessageWidget

class AIWorker (QThread ):
   
    response_received =pyqtSignal (str ,dict )
    error_occurred =pyqtSignal (str )

    def __init__ (self ,user_message ,token ):
        super ().__init__ ()
        self .user_message =user_message
        self .token =token
        self .is_cancelled =False

    def cancel (self ):
        self .is_cancelled =True

    def run (self ):
        try :
            if self .is_cancelled :
                return


            headers ={
            'Authorization':f'Bearer {self .token }',
            'Content-Type':'application/json'
            }

            data ={
            'message':self .user_message ,
            'model':Config .AI_MODEL_TECHNICAL
            }


            print (f"🤖 Sending AI request to {Config .AI_MODEL_DISPLAY }: {self .user_message [:50 ]}...")

            if self .is_cancelled :
                return

            response =requests .post (
            'https://api.emailsec.shop/api/ai/chat',
            headers =headers ,
            json =data ,
            timeout =30
            )

            if self .is_cancelled :
                return

            if response .ok :
                result =response .json ()
                ai_response =result .get ('response','No response received')


                metadata ={
                'model_used':result .get ('model_used','Unknown'),
                'credits_remaining':result .get ('credits_remaining',0 ),
                'tokens_used':result .get ('usage',{}).get ('total_tokens',0 )
                }


                self .response_received .emit (ai_response ,metadata )

            else :

                error_data =response .json ()if response .content else {}
                error_code =error_data .get ('code','')
                error_msg =error_data .get ('error','Unknown error')

                print (f"❌ AI request failed: {error_msg } (Code: {error_code })")


                if error_code =='INSUFFICIENT_CREDITS':
                    error_response ="💳 You've run out of credits! Please contact support to add more credits to your account."
                elif error_code =='RATE_LIMIT_EXCEEDED':
                    error_response ="⏱️ You're sending messages too quickly. Please wait a moment and try again."
                elif error_code =='UNSAFE_CONTENT':
                    error_response ="🛡️ Your message was blocked by our safety filters. Please rephrase your question in a more appropriate way."
                elif error_code =='UNSAFE_RESPONSE':
                    error_response ="🤖 I apologize, but I couldn't generate a safe response to your request. Please try rephrasing your question or asking about a different topic."
                elif error_code =='ACCOUNT_BANNED':
                    error_response ="🚫 Your account has been suspended due to policy violations. Please contact support."
                else :
                    error_response =f"❌ AI service error: {error_msg }. Please try again later."

                self .error_occurred .emit (error_response )

        except requests .exceptions .ConnectionError :
            if not self .is_cancelled :
                error_response ="🔌 Cannot connect to AI service. Please check your internet connection and try again."
                self .error_occurred .emit (error_response )
                print ("❌ Connection error: Cannot reach backend AI service")

        except requests .exceptions .Timeout :
            if not self .is_cancelled :
                error_response ="⏱️ AI request timed out. The service might be busy. Please try again."
                self .error_occurred .emit (error_response )
                print ("❌ Timeout error: AI request took too long")

        except Exception as e :
            if not self .is_cancelled :
                error_response =f"❌ Unexpected error: {str (e )}. Please try again."
                self .error_occurred .emit (error_response )
                print (f"❌ Unexpected error in AI request: {str (e )}")

class MessageWidget (QWidget ):

    def __init__ (self ,sender ,content ,timestamp ):
        super ().__init__ ()
        self .sender =sender
        self .content =content
        self .timestamp =timestamp
        self .setup_ui ()

    def setup_ui (self ):

        main_layout =QHBoxLayout ()
        main_layout .setContentsMargins (15 ,5 ,15 ,5 )
        main_layout .setSpacing (0 )


        bubble_container =QWidget ()
        bubble_layout =QVBoxLayout (bubble_container )
        bubble_layout .setContentsMargins (15 ,12 ,15 ,12 )
        bubble_layout .setSpacing (5 )



        formatted_content =TextFormatter .format_comprehensive (self .content ,self .sender )
        content_label =QLabel (formatted_content )
        content_label .setWordWrap (True )
        content_label .setTextInteractionFlags (Qt .TextSelectableByMouse )

        content_label .setTextFormat (Qt .RichText )


        content_label .setSizePolicy (QSizePolicy .Preferred ,QSizePolicy .Minimum )


        content_label .setMaximumWidth (300 )


        time_label =QLabel (self .format_timestamp ())
        time_label .setSizePolicy (QSizePolicy .Preferred ,QSizePolicy .Fixed )


        bubble_layout .addWidget (content_label )
        bubble_layout .addWidget (time_label )


        bubble_container .setMaximumWidth (330 )


        if self .sender =='user':

            main_layout .addStretch ()
            main_layout .addWidget (bubble_container )


            bubble_container .setStyleSheet (f"""
                QWidget {{
                    background: {Config .ACCENT_GRADIENT };
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }}
            """)


            content_label .setStyleSheet (f"""
                QLabel {{
                    color: #1a1a1a;
                    font-size: {Config .FONT_SIZE_MEDIUM }px;
                    line-height: 1.4;
                    font-weight: 600;
                    font-family: '{Config .FONT_FAMILY }';
                    background: transparent;
                    padding: 2px 0px;
                }}
            """)


            time_label .setStyleSheet (f"""
                QLabel {{
                    color: rgba(26, 26, 26, 0.7);
                    font-size: {Config .FONT_SIZE_SMALL }px;
                    font-weight: 500;
                    background: transparent;
                }}
            """)
            time_label .setAlignment (Qt .AlignRight )

        else :

            main_layout .addWidget (bubble_container )
            main_layout .addStretch ()


            bubble_container .setStyleSheet (f"""
                QWidget {{
                    background: rgba(255, 255, 255, 0.15);
                    border: none;
                    border-radius: 18px;
                    margin: 3px 0px;
                }}
            """)


            content_label .setStyleSheet (f"""
                QLabel {{
                    color: white;
                    font-size: {Config .FONT_SIZE_MEDIUM }px;
                    line-height: 1.4;
                    font-weight: 600;
                    font-family: '{Config .FONT_FAMILY }';
                    background: transparent;
                    padding: 2px 0px;
                }}
            """)


            time_label .setStyleSheet (f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.7);
                    font-size: {Config .FONT_SIZE_SMALL }px;
                    font-weight: 500;
                    background: transparent;
                }}
            """)
            time_label .setAlignment (Qt .AlignLeft )

        self .setLayout (main_layout )

    def format_timestamp (self ):
        try :
            if isinstance (self .timestamp ,str ):
                dt =datetime .fromisoformat (self .timestamp .replace ('Z','+00:00'))
            else :
                dt =self .timestamp

            now =datetime .now ()
            if dt .date ()==now .date ():
                return dt .strftime ("%H:%M")
            else :
                return dt .strftime ("%m/%d %H:%M")
        except :
            return "Now"

class TypingIndicator (QWidget ):

    def __init__ (self ):
        super ().__init__ ()
        self .timer =None
        self .label =None
        self .dot_count =0
        self .is_destroyed =False
        self .setup_ui ()
        self .setup_animation ()

    def setup_ui (self ):

        main_layout =QHBoxLayout ()
        main_layout .setContentsMargins (15 ,5 ,15 ,5 )
        main_layout .setSpacing (0 )


        bubble_container =QWidget ()
        bubble_layout =QHBoxLayout (bubble_container )
        bubble_layout .setContentsMargins (15 ,12 ,15 ,12 )
        bubble_layout .setSpacing (0 )


        self .label =QLabel (f"🐛 {Config .AI_MODEL_DISPLAY } is thinking")
        self .label .setWordWrap (False )
        self .label .setStyleSheet (f"""
            QLabel {{
                color: white;
                font-style: italic;
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                font-weight: 600;
                background: transparent;
                font-family: '{Config .FONT_FAMILY }';
                white-space: nowrap;
            }}
        """)

        bubble_layout .addWidget (self .label )


        bubble_container .setMaximumWidth (450 )


        bubble_container .setStyleSheet (f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.15);
                border: none;
                border-radius: 18px;
                margin: 3px 0px;
            }}
        """)


        main_layout .addWidget (bubble_container )
        main_layout .addStretch ()

        self .setLayout (main_layout )

    def setup_animation (self ):
        self .timer =QTimer (self )
        self .timer .timeout .connect (self .animate_dots )
        self .timer .start (500 )
        self .dot_count =0

    def animate_dots (self ):

        if self .is_destroyed or not self .label :
            return

        try :
            dots ="."*(self .dot_count %4 )
            self .label .setText (f"🐛 {Config .AI_MODEL_DISPLAY } is thinking{dots }")
            self .dot_count +=1
        except RuntimeError :

            self .stop_animation ()

    def stop_animation (self ):
        if self .timer and self .timer .isActive ():
            self .timer .stop ()

    def closeEvent (self ,event ):
        self .is_destroyed =True
        self .stop_animation ()
        super ().closeEvent (event )

    def deleteLater (self ):
        self .is_destroyed =True
        self .stop_animation ()
        super ().deleteLater ()

class MainWindow (QMainWindow ):

    logout_requested =pyqtSignal ()

    def __init__ (self ,user_data ):
        super ().__init__ ()
        self .user_data =user_data
        self .db_manager =DatabaseManager ()
        self .session_manager =SessionManager ()
        self .current_conversation_id =None
        self .typing_indicator =None
        self .drag_position =None
        self .chat_items ={}
        self .selected_chat_item =None
        self .ai_worker =None

        self .setup_window ()
        self .setup_ui ()
        self .load_conversations ()
        self .setup_session_validation (skip_initial_validation =True )

    def setup_window (self ):
        self .setWindowTitle ("🐛 Black Worm - The Dark AI Agent")
        self .setMinimumSize (Config .WINDOW_MIN_WIDTH ,Config .WINDOW_MIN_HEIGHT )
        self .resize (1200 ,800 )


        self .setWindowFlags (Qt .FramelessWindowHint )
        self .setAttribute (Qt .WA_TranslucentBackground )


        screen =QApplication .desktop ().availableGeometry ()
        self .move (
        (screen .width ()-self .width ())//2 ,
        (screen .height ()-self .height ())//2
        )

    def setup_ui (self ):
        central_widget =QWidget ()
        self .setCentralWidget (central_widget )

        main_layout =QVBoxLayout (central_widget )
        main_layout .setContentsMargins (0 ,0 ,0 ,0 )
        main_layout .setSpacing (0 )


        self .create_title_bar (main_layout )


        content_splitter =QSplitter (Qt .Horizontal )
        content_splitter .setHandleWidth (3 )
        content_splitter .setStyleSheet (f"""
            QSplitter::handle {{
                background-color: {Config .ACCENT_COLOR };
                border: none;
                margin: 10px 0px;
            }}
            QSplitter::handle:hover {{
                background-color: #00ffff;
            }}
        """)


        self .create_sidebar (content_splitter )
        self .create_chat_area (content_splitter )


        content_splitter .setSizes ([300 ,900 ])
        content_splitter .setStretchFactor (0 ,0 )
        content_splitter .setStretchFactor (1 ,1 )

        main_layout .addWidget (content_splitter )


        central_widget .setStyleSheet ("background: transparent;")

    def create_title_bar (self ,main_layout ):
        title_bar =QFrame ()
        title_bar .setFixedHeight (60 )
        title_bar .setObjectName ("titleBar")

        title_layout =QHBoxLayout (title_bar )
        title_layout .setContentsMargins (25 ,0 ,20 ,0 )


        title_label =QLabel ("🐛 Black Worm - The Dark AI Agent")
        title_label .setObjectName ("appTitle")
        title_label .setStyleSheet (f"""
            QLabel {{
                color: {Config .ACCENT_COLOR };
                font-size: {Config .FONT_SIZE_TITLE }px;
                font-weight: 800;
                font-family: '{Config .FONT_FAMILY }';
                background: transparent;
            }}
        """)

        title_layout .addWidget (title_label )
        title_layout .addStretch ()


        self .profile_btn =QPushButton (f"👤 {self .user_data ['username']}")
        self .profile_btn .setObjectName ("profileButton")
        self .profile_btn .clicked .connect (self .show_profile_menu )
        self .profile_btn .setStyleSheet (f"""
            QPushButton {{
                background: {Config .ACCENT_GRADIENT };
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                color: white;
                font-size: {Config .FONT_SIZE_NORMAL }px;
                font-weight: 600;
                font-family: '{Config .FONT_FAMILY }';
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #00ccff);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ccff, stop:1 #0099ff);
            }}
        """)


        minimize_btn =QPushButton ("−")
        minimize_btn .setFixedSize (40 ,30 )
        minimize_btn .setObjectName ("minimizeButton")
        minimize_btn .clicked .connect (self .showMinimized )

        close_btn =QPushButton ("×")
        close_btn .setFixedSize (40 ,30 )
        close_btn .setObjectName ("closeButton")
        close_btn .clicked .connect (self .close )


        control_style =f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: {Config .TEXT_COLOR };
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid {Config .ACCENT_COLOR };
            }}
        """
        minimize_btn .setStyleSheet (control_style )
        close_btn .setStyleSheet (control_style +"""
            QPushButton:hover {
                background: #ff4444;
                border: 1px solid #ff6666;
            }
        """)

        title_layout .addWidget (self .profile_btn )
        title_layout .addWidget (minimize_btn )
        title_layout .addWidget (close_btn )


        title_bar .setStyleSheet ("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)

        main_layout .addWidget (title_bar )

    def create_sidebar (self ,parent ):
        sidebar =QFrame ()
        sidebar .setFixedWidth (300 )
        sidebar .setObjectName ("sidebar")

        sidebar_layout =QVBoxLayout (sidebar )
        sidebar_layout .setContentsMargins (20 ,20 ,20 ,20 )
        sidebar_layout .setSpacing (15 )


        new_chat_btn =QPushButton ("+ New Chat")
        new_chat_btn .setObjectName ("newChatButton")
        new_chat_btn .clicked .connect (self .create_new_conversation )
        new_chat_btn .setStyleSheet (f"""
            QPushButton {{
                background: {Config .ACCENT_GRADIENT };
                border: 2px solid {Config .ACCENT_COLOR };
                border-radius: 18px;
                padding: 18px 25px;
                color: #1a1a1a;
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                font-weight: 700;
                font-family: '{Config .FONT_FAMILY }';
                margin: 5px 0px;
            }}
            QPushButton:hover {{
                background: {Config .NEON_GRADIENT };
                border: 2px solid #00ffff;
                color: #1a1a1a;
            }}
            QPushButton:pressed {{
                background: {Config .TEAL_GRADIENT };
                border: 2px solid #00bcd4;
                color: #1a1a1a;
            }}
        """)


        self .chats_scroll =QScrollArea ()
        self .chats_scroll .setWidgetResizable (True )
        self .chats_scroll .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        self .chats_scroll .setVerticalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        self .chats_scroll .setObjectName ("chatsScroll")


        self .chats_container =QWidget ()
        self .chats_layout =QVBoxLayout (self .chats_container )
        self .chats_layout .setContentsMargins (5 ,5 ,5 ,5 )
        self .chats_layout .setSpacing (5 )
        self .chats_layout .addStretch ()

        self .chats_scroll .setWidget (self .chats_container )


        self .chats_scroll .setStyleSheet (f"""
            QScrollArea {{
                background: transparent;
                border: none;
                outline: none;
            }}
        """)

        sidebar_layout .addWidget (new_chat_btn )


        recent_label =QLabel ("Recent Chats")
        recent_label .setObjectName ("recentChatsLabel")
        recent_label .setStyleSheet (f"""
            QLabel {{
                color: white;
                font-size: {Config .FONT_SIZE_LARGE }px;
                font-weight: 700;
                font-family: '{Config .FONT_FAMILY }';
                margin: 15px 0px 10px 0px;
                padding: 8px 0px;
                background: transparent;
            }}
        """)
        sidebar_layout .addWidget (recent_label )


        separator_line =QFrame ()
        separator_line .setFrameShape (QFrame .HLine )
        separator_line .setFrameShadow (QFrame .Sunken )
        separator_line .setStyleSheet (f"""
            QFrame {{
                background-color: {Config .ACCENT_COLOR };
                border: none;
                height: 2px;
                margin: 5px 0px 15px 0px;
            }}
        """)
        sidebar_layout .addWidget (separator_line )

        sidebar_layout .addWidget (self .chats_scroll )


        sidebar .setStyleSheet (f"""
            QFrame#sidebar {{
                background: {Config .SIDEBAR_GRADIENT };
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-right: 2px solid {Config .ACCENT_COLOR };
                border-radius: 15px 0px 0px 15px;
                margin: 5px 0px 5px 5px;
            }}
        """)

        parent .addWidget (sidebar )

    def create_chat_area (self ,parent ):
        chat_area =QFrame ()
        chat_area .setObjectName ("chatArea")

        chat_layout =QVBoxLayout (chat_area )
        chat_layout .setContentsMargins (0 ,0 ,0 ,0 )
        chat_layout .setSpacing (0 )


        self .messages_scroll =QScrollArea ()
        self .messages_scroll .setWidgetResizable (True )
        self .messages_scroll .setHorizontalScrollBarPolicy (Qt .ScrollBarAlwaysOff )
        self .messages_scroll .setVerticalScrollBarPolicy (Qt .ScrollBarAsNeeded )
        self .messages_scroll .setObjectName ("messagesScroll")

        self .messages_widget =QWidget ()
        self .messages_layout =QVBoxLayout (self .messages_widget )
        self .messages_layout .setContentsMargins (15 ,15 ,15 ,15 )
        self .messages_layout .setSpacing (5 )
        self .messages_layout .addStretch ()

        self .messages_scroll .setWidget (self .messages_widget )


        input_frame =QFrame ()
        input_frame .setFixedHeight (80 )
        input_frame .setObjectName ("inputFrame")

        input_layout =QHBoxLayout (input_frame )
        input_layout .setContentsMargins (20 ,15 ,20 ,15 )
        input_layout .setSpacing (12 )


        self .message_input =QLineEdit ()
        self .message_input .setPlaceholderText ("Type your message here...")
        self .message_input .setObjectName ("messageInput")


        self .message_input .setSizePolicy (QSizePolicy .Expanding ,QSizePolicy .Fixed )
        self .message_input .setFixedHeight (50 )

        self .message_input .setStyleSheet (f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.08);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                padding: 12px 20px;
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                color: {Config .TEXT_COLOR };
                font-weight: 500;
                font-family: '{Config .FONT_FAMILY }';
                selection-background-color: {Config .ACCENT_COLOR };
            }}
            QLineEdit:focus {{
                border: 2px solid {Config .ACCENT_COLOR };
                background: rgba(255, 255, 255, 0.12);
                outline: none;
            }}
            QLineEdit:hover {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(0, 245, 255, 0.3);
            }}
        """)


        self .send_btn =QPushButton ("Send")
        self .send_btn .setFixedSize (80 ,50 )
        self .send_btn .setObjectName ("sendButton")
        self .send_btn .clicked .connect (self .send_message )


        self .send_btn .setSizePolicy (QSizePolicy .Fixed ,QSizePolicy .Fixed )

        self .send_btn .setStyleSheet (f"""
            QPushButton {{
                background: {Config .ACCENT_GRADIENT };
                border: none;
                border-radius: 25px;
                color: #1a1a1a;
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                font-weight: 700;
                font-family: '{Config .FONT_FAMILY }';
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
                color: rgba(255, 255, 255, 0.5);
            }}
        """)


        self .message_input .returnPressed .connect (self .send_message )


        input_layout .addWidget (self .message_input )
        input_layout .addWidget (self .send_btn )

        chat_layout .addWidget (self .messages_scroll )
        chat_layout .addWidget (input_frame )


        chat_area .setStyleSheet (f"""
            QFrame#chatArea {{
                background: {Config .MODERN_GRADIENT_2 };
                border: 1px solid rgba(0, 245, 255, 0.2);
                border-radius: 15px;
                margin: 5px;
            }}
            QScrollArea#messagesScroll {{
                background: transparent;
                border: none;
                border-radius: 10px;
            }}
            QWidget {{
                background: transparent;
            }}
            QFrame#inputFrame {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 245, 255, 0.3);
                border-radius: 15px;
                margin: 5px;
            }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {Config .ACCENT_COLOR };
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #00ffff;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

        parent .addWidget (chat_area )

    def paintEvent (self ,event ):
        super ().paintEvent (event )

        painter =QPainter (self )
        painter .setRenderHint (QPainter .Antialiasing )


        gradient =QLinearGradient (0 ,0 ,self .width (),self .height ())
        gradient .setColorAt (0 ,QColor ("#0a0a0a"))
        gradient .setColorAt (0.3 ,QColor ("#1a1a1a"))
        gradient .setColorAt (0.7 ,QColor ("#2d2d2d"))
        gradient .setColorAt (1 ,QColor ("#0a0a0a"))


        painter .fillRect (self .rect (),QBrush (gradient ))


        pen =QPen (QColor (Config .ACCENT_COLOR ),3 )
        painter .setPen (pen )
        painter .drawRoundedRect (self .rect ().adjusted (1 ,1 ,-1 ,-1 ),20 ,20 )


        inner_pen =QPen (QColor (Config .ACCENT_COLOR ))
        inner_pen .setWidth (1 )
        painter .setPen (inner_pen )
        painter .drawRoundedRect (self .rect ().adjusted (4 ,4 ,-4 ,-4 ),17 ,17 )

    def add_message_widget (self ,sender ,content ,timestamp ):
        message_widget =EnhancedMessageWidget (sender ,content ,timestamp )


        self .messages_layout .insertWidget (self .messages_layout .count ()-1 ,message_widget )


        QTimer .singleShot (100 ,self .scroll_to_bottom )

    def show_typing_indicator (self ):
        if self .typing_indicator is None :
            self .typing_indicator =TypingIndicator ()
            self .messages_layout .insertWidget (self .messages_layout .count ()-1 ,self .typing_indicator )
            QTimer .singleShot (100 ,self .scroll_to_bottom )

    def hide_typing_indicator (self ):
        if self .typing_indicator :
            try :

                self .typing_indicator .stop_animation ()


                self .messages_layout .removeWidget (self .typing_indicator )


                self .typing_indicator .deleteLater ()


                self .typing_indicator =None

            except RuntimeError as e :

                print (f"⚠️ TypingIndicator already deleted: {e }")
                self .typing_indicator =None
            except Exception as e :
                print (f"❌ Error hiding typing indicator: {e }")
                self .typing_indicator =None

    def scroll_to_bottom (self ):
        scrollbar =self .messages_scroll .verticalScrollBar ()
        scrollbar .setValue (scrollbar .maximum ())

    def send_message (self ):
        message_text =self .message_input .text ().strip ()
        if not message_text :
            return


        self .send_btn .setEnabled (False )


        self .message_input .clear ()


        if not self .current_conversation_id :
            self .current_conversation_id =self .db_manager .create_conversation ()


        try :
            self .db_manager .add_message (self .current_conversation_id ,'user',message_text )

            self .move_conversation_to_top (self .current_conversation_id )
        except Exception as e :
            print (f"❌ Error saving user message: {e }")


        self .add_message_widget ('user',message_text ,datetime .now ())


        self .show_typing_indicator ()


        self .get_ai_response (message_text )

    def get_ai_response (self ,user_message ):
        try :

            user_data =self .session_manager .get_user_data ()
            if not user_data or not user_data .get ('token'):
                self .hide_typing_indicator ()
                self .send_btn .setEnabled (True )
                error_response ="❌ Authentication required. Please login again."
                self .add_message_widget ('ai',error_response ,datetime .now ())
                return

            token =user_data ['token']


            if self .ai_worker and self .ai_worker .isRunning ():
                self .ai_worker .cancel ()
                self .ai_worker .wait (1000 )


            self .ai_worker =AIWorker (user_message ,token )
            self .ai_worker .response_received .connect (self .on_ai_response_received )
            self .ai_worker .error_occurred .connect (self .on_ai_error_occurred )
            self .ai_worker .finished .connect (self .on_ai_worker_finished )
            self .ai_worker .start ()

        except Exception as e :
            self .hide_typing_indicator ()
            self .send_btn .setEnabled (True )
            error_response =f"❌ Unexpected error: {str (e )}. Please try again."
            self .add_message_widget ('ai',error_response ,datetime .now ())
            print (f"❌ Unexpected error starting AI worker: {str (e )}")

    def on_ai_response_received (self ,ai_response ,metadata ):
        try :

            self .hide_typing_indicator ()


            model_used =metadata .get ('model_used','Unknown')

            if model_used in [Config .AI_MODEL_TECHNICAL ,'mistralai/mistral-nemotron']:
                display_model =Config .AI_MODEL_DISPLAY
            else :
                display_model =model_used

            credits_remaining =metadata .get ('credits_remaining',0 )
            tokens_used =metadata .get ('tokens_used',0 )

            print (f"✅ AI Response received (Model: {display_model }, Credits: {credits_remaining }, Tokens: {tokens_used })")


            self .session_manager .update_credits (credits_remaining )
            print (f"🔄 Credits updated in session: {credits_remaining }")


            try :
                self .db_manager .add_message (self .current_conversation_id ,'ai',ai_response )

                self .move_conversation_to_top (self .current_conversation_id )
            except Exception as e :
                print (f"❌ Error saving AI message: {e }")


            self .add_message_widget ('ai',ai_response ,datetime .now ())

        except Exception as e :
            print (f"❌ Error handling AI response: {str (e )}")
            self .add_message_widget ('ai',f"❌ Error processing response: {str (e )}",datetime .now ())

    def on_ai_error_occurred (self ,error_message ):
        try :

            self .hide_typing_indicator ()


            self .add_message_widget ('ai',error_message ,datetime .now ())

        except Exception as e :
            print (f"❌ Error handling AI error: {str (e )}")

    def on_ai_worker_finished (self ):
        try :

            self .send_btn .setEnabled (True )


            if self .ai_worker :
                self .ai_worker .deleteLater ()
                self .ai_worker =None

        except Exception as e :
            print (f"❌ Error cleaning up AI worker: {str (e )}")

            self .send_btn .setEnabled (True )

    def create_new_conversation (self ):
        try :

            self .current_conversation_id =self .db_manager .create_conversation ()


            self .clear_messages ()
            if self .selected_chat_item :
                self .selected_chat_item .set_selected (False )
                self .selected_chat_item =None


            self .refresh_recent_chats ()


            if self .current_conversation_id in self .chat_items :
                self .update_selected_chat_item (self .current_conversation_id )


            welcome_msg ="Hello! I'm Black Worm, your AI assistant. How can I help you today?"
            self .add_message_widget ('ai',welcome_msg ,datetime .now ())

            print (f"✅ New conversation created: {self .current_conversation_id }")

        except Exception as e :
            print (f"❌ Error creating new conversation: {e }")

            self .current_conversation_id =None
            self .clear_messages ()
            error_msg ="Started a temporary chat session. Your messages won't be saved."
            self .add_message_widget ('ai',error_msg ,datetime .now ())

    def clear_messages (self ):

        self .hide_typing_indicator ()


        while self .messages_layout .count ()>1 :
            child =self .messages_layout .takeAt (0 )
            if child .widget ():
                child .widget ().deleteLater ()

    def load_conversations (self ):
        try :

            self .clear_chat_items ()


            conversations =self .db_manager .get_conversations ()

            if not conversations :

                self .show_empty_chats_message ()
                return


            for conv in conversations :
                self .add_chat_item (conv ['id'],conv ['title'],conv ['updated_at'])

        except Exception as e :
            print (f"❌ Error loading conversations: {e }")
            self .show_empty_chats_message ()

    def load_conversation (self ,conversation_id ):
        try :

            self .clear_messages ()


            self .current_conversation_id =conversation_id


            self .update_selected_chat_item (conversation_id )


            messages =self .db_manager .get_conversation_messages (conversation_id )

            if messages :

                for msg in messages :
                    self .add_message_widget (msg ['sender'],msg ['content'],msg ['timestamp'])
            else :

                welcome_msg ="Hello! How can I help you today?"
                self .add_message_widget ('ai',welcome_msg ,datetime .now ())

        except Exception as e :
            print (f"❌ Error loading conversation: {e }")

            error_msg ="Sorry, there was an error loading this conversation."
            self .add_message_widget ('ai',error_msg ,datetime .now ())

    def add_chat_item (self ,conversation_id ,title ,updated_at ):

        chat_item =ChatItemWidget (conversation_id ,title ,updated_at )


        chat_item .chat_selected .connect (self .load_conversation )
        chat_item .chat_deleted .connect (self .delete_conversation )


        self .chats_layout .insertWidget (0 ,chat_item )


        self .chat_items [conversation_id ]=chat_item

    def clear_chat_items (self ):

        while self .chats_layout .count ()>1 :
            child =self .chats_layout .takeAt (0 )
            if child .widget ():
                child .widget ().deleteLater ()


        self .chat_items .clear ()
        self .selected_chat_item =None

    def show_empty_chats_message (self ):
        empty_label =QLabel ("No recent chats\nStart a new conversation!")
        empty_label .setAlignment (Qt .AlignCenter )
        empty_label .setStyleSheet (f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.6);
                font-size: {Config .FONT_SIZE_NORMAL }px;
                font-family: '{Config .FONT_FAMILY }';
                font-style: italic;
                font-weight: 500;
                padding: 20px;
                background: transparent;
            }}
        """)
        self .chats_layout .insertWidget (0 ,empty_label )

    def update_selected_chat_item (self ,conversation_id ):

        if self .selected_chat_item :
            self .selected_chat_item .set_selected (False )


        if conversation_id in self .chat_items :
            self .selected_chat_item =self .chat_items [conversation_id ]
            self .selected_chat_item .set_selected (True )

    def delete_conversation (self ,conversation_id ):

        reply =self .show_custom_message_box (
        "Delete Conversation",
        "Are you sure you want to delete this conversation?\nThis action cannot be undone.",
        "🗑️",
        QMessageBox .Yes |QMessageBox .No
        )

        if reply ==QMessageBox .Yes :
            try :

                success =self .db_manager .delete_conversation (conversation_id )

                if success :

                    if conversation_id in self .chat_items :
                        chat_item =self .chat_items [conversation_id ]
                        self .chats_layout .removeWidget (chat_item )
                        chat_item .deleteLater ()
                        del self .chat_items [conversation_id ]


                    if self .current_conversation_id ==conversation_id :
                        self .current_conversation_id =None
                        self .clear_messages ()
                        self .selected_chat_item =None


                        welcome_msg ="Conversation deleted. Start a new chat!"
                        self .add_message_widget ('ai',welcome_msg ,datetime .now ())


                    if not self .chat_items :
                        self .show_empty_chats_message ()

                    print (f"✅ Conversation deleted successfully")
                else :
                    self .show_custom_message_box (
                    "Error",
                    "Failed to delete conversation.",
                    "❌"
                    )

            except Exception as e :
                print (f"❌ Error deleting conversation: {e }")
                self .show_custom_message_box (
                "Error",
                f"Error deleting conversation: {str (e )}",
                "❌"
                )

    def refresh_recent_chats (self ):
        try :

            current_selection =self .current_conversation_id


            self .load_conversations ()


            if current_selection and current_selection in self .chat_items :
                self .update_selected_chat_item (current_selection )

        except Exception as e :
            print (f"❌ Error refreshing recent chats: {e }")

    def move_conversation_to_top (self ,conversation_id ):
        try :
            if conversation_id not in self .chat_items :

                self .refresh_recent_chats ()
                return


            chat_item =self .chat_items [conversation_id ]


            self .chats_layout .removeWidget (chat_item )


            self .chats_layout .insertWidget (0 ,chat_item )


            conversations =self .db_manager .get_conversations ()
            for conv in conversations :
                if conv ['id']==conversation_id :
                    chat_item .update_title (conv ['title'])
                    chat_item .update_timestamp (conv ['updated_at'])
                    break

        except Exception as e :
            print (f"❌ Error moving conversation to top: {e }")

            self .refresh_recent_chats ()

    def show_custom_message_box (self ,title ,message ,icon_emoji ="ℹ️",buttons =QMessageBox .Ok ):
        msg_box =QMessageBox (self )
        msg_box .setWindowTitle ('')
        msg_box .setText (f'{icon_emoji } {title }')
        msg_box .setInformativeText (message )
        msg_box .setStandardButtons (buttons )
        msg_box .setIcon (QMessageBox .NoIcon )


        msg_box .setWindowFlags (Qt .FramelessWindowHint |Qt .Dialog )



        msg_box .setStyleSheet (f"""
            QMessageBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 15, 15, 1.0),
                    stop:0.5 rgba(30, 30, 30, 1.0),
                    stop:1 rgba(15, 15, 15, 1.0));
                border: 2px solid {Config .ACCENT_COLOR };
                border-radius: 20px;
                color: {Config .TEXT_COLOR };
                font-family: '{Config .FONT_FAMILY }';
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                padding: 20px;
                min-width: 350px;
            }}
            QMessageBox QLabel {{
                color: {Config .TEXT_COLOR };
                font-size: {Config .FONT_SIZE_MEDIUM }px;
                font-weight: 600;
                padding: 10px;
                background: transparent;
                border: none;
            }}
            QMessageBox QPushButton {{
                background: {Config .ACCENT_GRADIENT };
                border: 2px solid {Config .ACCENT_COLOR };
                border-radius: 12px;
                padding: 12px 24px;
                color: #1a1a1a;
                font-weight: 700;
                font-size: {Config .FONT_SIZE_NORMAL }px;
                min-width: 80px;
                margin: 5px;
            }}
            QMessageBox QPushButton:hover {{
                background: {Config .NEON_GRADIENT };
                border: 2px solid #00ffff;
            }}
            QMessageBox QPushButton:pressed {{
                background: {Config .TEAL_GRADIENT };
                border: 2px solid #00bcd4;
            }}
            QMessageBox QPushButton[text="No"] {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: {Config .TEXT_COLOR };
            }}
            QMessageBox QPushButton[text="No"]:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
                color: white;
            }}
            QMessageBox QPushButton[text="Cancel"] {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: {Config .TEXT_COLOR };
            }}
            QMessageBox QPushButton[text="Cancel"]:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.5);
                color: white;
            }}
        """)

        return msg_box .exec_ ()

    def show_profile_menu (self ):
        menu =QMenu (self )
        menu .setStyleSheet (f"""
            QMenu {{
                background: {Config .MODERN_GRADIENT_1 };
                border: 2px solid {Config .ACCENT_COLOR };
                border-radius: 10px;
                padding: 8px;
                color: {Config .TEXT_COLOR };
                font-size: {Config .FONT_SIZE_NORMAL }px;
                font-family: '{Config .FONT_FAMILY }';
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px;
            }}
            QMenu::item:selected {{
                background: {Config .ACCENT_GRADIENT };
                color: white;
            }}
        """)

        menu .addAction ("Account Info",self .show_account_info )
        menu .addAction ("💳 Buy Credits",self .show_buy_credits )
        menu .addSeparator ()
        menu .addAction ("Logout",self .logout )

        menu .exec_ (self .profile_btn .mapToGlobal (self .profile_btn .rect ().bottomLeft ()))

    def setup_session_validation (self ,skip_initial_validation =False ):
        from PyQt5 .QtCore import QTimer
        from utils .session_manager import SessionManager

        self .session_manager =SessionManager ()


        self .session_timer =QTimer ()
        self .session_timer .timeout .connect (self .validate_session )
        self .session_timer .start (300000 )


        if not skip_initial_validation :
            self .validate_session ()

    def validate_session (self ):
        try :

            if not self .session_manager .has_valid_session ():
                print ("❌ No active session found")
                self .logout_requested .emit ()
                return


            user_data =self .session_manager .get_user_data ()
            if not user_data or not user_data .get ('token'):
                print ("❌ No valid token in session")
                self .logout_requested .emit ()
                return


            is_valid ,response =self .session_manager .validate_session_with_server ()
            if not is_valid :
                error_msg =response .get ('error','Unknown error')
                print (f"❌ Session validation failed: {error_msg }")


                if any (keyword in error_msg .lower ()for keyword in ['token','jwt','malformed','invalid']):
                    print ("🔄 Token issue detected, clearing session and redirecting to login")
                    self .session_manager .clear_session ()

                self .logout_requested .emit ()
                return


            if user_data :
                self .user_data =user_data

                if hasattr (self ,'profile_btn'):
                    self .profile_btn .setText (f"👤 {user_data .get ('username','User')}")
                print ("✅ Session validation successful")

        except Exception as e :
            print (f"❌ Session validation error: {e }")

            if "token"in str (e ).lower ()or "jwt"in str (e ).lower ():
                print ("🔄 Critical token error, clearing session")
                self .session_manager .clear_session ()
                self .logout_requested .emit ()

    def logout (self ):

        if hasattr (self ,'session_timer'):
            self .session_timer .stop ()


        if hasattr (self ,'session_manager'):
            self .session_manager .clear_session ()

        self .logout_requested .emit ()

    def show_account_info (self ):
        try :
            from ui .account_info_dialog import AccountInfoDialog
            dialog =AccountInfoDialog (self )
            dialog .exec_ ()
        except Exception as e :
            print (f"❌ Error showing account info: {e }")

            from PyQt5 .QtWidgets import QMessageBox
            QMessageBox .warning (self ,"Error",f"Failed to load account information:\n{str (e )}")

    def show_buy_credits (self ):
        try :
            print ("🔄 Opening credit purchase dialog...")
            dialog =CreditPurchaseDialog (self .user_data ,self )
            result =dialog .exec_ ()

            if result ==dialog .Accepted :
                print ("✅ Credit purchase dialog completed")



            else :
                print ("ℹ️ Credit purchase dialog cancelled")

        except Exception as e :
            print (f"❌ Error showing credit purchase dialog: {e }")

            from PyQt5 .QtWidgets import QMessageBox
            QMessageBox .warning (self ,"Error",f"Failed to load credit purchase dialog:\n{str (e )}")

    def eventFilter (self ,obj ,event ):
        return super ().eventFilter (obj ,event )

    def mousePressEvent (self ,event ):
        if event .button ()==Qt .LeftButton :
            self .drag_position =event .globalPos ()-self .frameGeometry ().topLeft ()
            event .accept ()

    def mouseMoveEvent (self ,event ):
        if event .buttons ()==Qt .LeftButton and self .drag_position :
            self .move (event .globalPos ()-self .drag_position )
            event .accept ()

    def closeEvent (self ,event ):
        try :

            if hasattr (self ,'session_timer'):
                self .session_timer .stop ()


            self .hide_typing_indicator ()


            if self .ai_worker and self .ai_worker .isRunning ():
                print ("🔄 Cancelling AI worker thread...")
                self .ai_worker .cancel ()
                self .ai_worker .wait (2000 )
                if self .ai_worker .isRunning ():
                    print ("⚠️ Force terminating AI worker thread...")
                    self .ai_worker .terminate ()
                    self .ai_worker .wait (1000 )
                self .ai_worker .deleteLater ()
                self .ai_worker =None

            print ("✅ Main window cleanup completed")

        except Exception as e :
            print (f"❌ Error during window cleanup: {e }")

        event .accept ()
