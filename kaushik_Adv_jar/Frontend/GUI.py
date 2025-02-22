from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QSpacerItem,QHBoxLayout
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars["Assistantname"]
cuurrent_dir = os.getcwd()
print(f"[DEBUG] Current directory: {cuurrent_dir}")
old_chat_message = ""
# kaushik_Adv_jar\Frontend\Files\Response.data
TempDirPath = rf"{cuurrent_dir}\kaushik_Adv_jar\Frontend\Files"
GraphicsDirPath = rf"{cuurrent_dir}\kaushik_Adv_jar\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["what", "where", "when", "why", "how", "who", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]+"?"
        else:
            new_query = new_query+"?"
            
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1]+"."
        else:
            new_query = new_query+"."
            
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding="utf-8") as file:
        file.write(Status)
        
def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding="utf-8") as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")
    
def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    path = rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Response.data', "w", encoding="utf-8") as file:
        print(TempDirectoryPath('Response.data'))
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self) .__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        # layout.setContentsMargins(20, 20, 20, 20)  # Adjust margins for centering
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis (1).gif'))
        max_gif_size_W = 480 #320 
        max_gif_size_H = 270 #180 
        
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        # self.gif_label.setAlignment(Qt.AlignRight)  # Center the GIF
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label, alignment=Qt.AlignCenter)  # Add centered GIF to layout
        # layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px;margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeachRecogText)
        self.timer.start(500)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
                QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
                }
                
                QScrollBar::handle:vertical {
                background: white;
                min-height: 2x0px;
                }
                
                QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
                }
                
                QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;   
                subcontrol-origin: margin;
                height: 10px;
                }
                
                QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
                }
                
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                }   
                """)
    def loadMessages(self):
            global old_chat_message
            # kaushik_Adv_jar\Frontend\Files\Response.data
            with open(TempDirectoryPath('Response.data'), "r", encoding='utf-8') as file:
                
                message = file.read()
                # print(f"[DEBUG] Message: {message}")
                
                # if not message or message == old_chat_message:
                #     return message
                
                # self.addMessage(message=message, color="white")
                # old_chat_message = message
                    
                if None == message:
                    pass
                
                elif len(message) <= 1:
                    pass
                
                elif str(old_chat_message) == str(message):
                    pass
                
                else:
                    self.addMessage(message=message, color= "white")
                    old_chat_message = message
                    
    def SpeachRecogText(self):
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                message = file.read()
                self.label.setText(message)
                
    def load_icon(self, path, width=60, height=60):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)
            
    def toggle_icon(self, event=None):
            if self.toggled:
                self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
                MicButtonInitialed()
                
            else:
                self.laod_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
                MicButtonClosed()
            self.toggled = not self.toggled
        
    def addMessage(self, message, color):
            cursor = self.chat_text_edit.textCursor()
            format = QTextCharFormat()
            formatm = QTextBlockFormat()
            formatm.setTopMargin(10)
            formatm.setLeftMargin(10)
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
            cursor.setBlockFormat(formatm)
            cursor.insertText(message + "\n")
            self.chat_text_edit.setTextCursor(cursor)
         
    
    
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super() .__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)  # Adjust margins for centering
        # content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis (1).gif'))
        # gif_label.setMovie(movie)
        max_gif_size_W = int(screen_width * 1)  # Reduce the width based on screen size
        max_gif_size_H = int(max_gif_size_W / 16*9)
        # max_gif_size_H = int(max_gif_size_W * 6 / 14)  # Maintain a 16:9 aspect ratio
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))

        # max_gif_size_H= int(screen_width / 16*9)
        # movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setMovie(movie)
        movie.start()
        
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on (1).png'))   
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150,150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self. label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px ; margin-bottom:0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        # content_layout.setContentsMargins(20, 20, 20, 20)  # Adjust margins for centering
        # 
        # close_button = QPushButton("Close")
        # close_button.setStyleSheet("background-color: red; color: white; font-size: 16px; padding: 10px;")
        # close_button.clicked.connect(self.close)
        # content_layout.addWidget(close_button, alignment=Qt.AlignCenter)
        # 
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on (1).png'), 60, 60)
            MicButtonInitialed()

        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off (1).png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled
        


class MessageScreen(QWidget):

    def __init__(self, parent=None):
            super() .__init__(parent)
            desktop = QApplication.desktop()
            screen_width = desktop.screenGeometry().width()
            screen_height = desktop.screenGeometry().height()
            layout = QVBoxLayout()
            label = QLabel("")
            layout.addWidget(label)
            chat_section = ChatSection()
            layout.addWidget(chat_section)
            self.setLayout(layout)
            self.setStyleSheet("background-color: black;")
            self.setFixedHeight(screen_height)
            self.setFixedWidth(screen_width)
            
class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
            super() .__init__(parent)
            self.parent = parent
            self.initUI()
            self.current_screen = None
            self.stacked_widget = stacked_widget

    def initUI(self):
            self.setFixedHeight(50)
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignRight)
            
            home_button = QPushButton()
            home_icon = QIcon(GraphicsDirectoryPath("Home (1).png"))
            home_button.setIcon(home_icon)
            home_button.setText(" Home")
            home_button.setStyleSheet("height:40px; line-height:40px ; background-color:white ; color: black")
            
            message_button = QPushButton()
            message_icon = QIcon(GraphicsDirectoryPath("Chats (1).png"))
            message_button.setIcon(message_icon)
            message_button.setText(" Chat")
            message_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")
            
            minimize_button = QPushButton()
            minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2 (1).png'))
            minimize_button.setIcon(minimize_icon)
            minimize_button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: white;
                }
                QPushButton:hover {
                    background-color: lightgray;
                }
                QPushButton:pressed {
                    background-color: gray;
                }
        """)
            minimize_button.clicked.connect(self.minimizeWindow)
            layout.addWidget(minimize_button)
            
            self.maximize_button = QPushButton()
            self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize (1).png'))
            self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize (1).png'))
            self.maximize_button.setIcon(self.maximize_icon)
            self.maximize_button.setFlat(False)
            # self.maximize_button.setStyleSheet("background-color: white; color: white;")
            self.maximize_button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: white;
                }""")
            # self.restore_icon.setStyleSheet("background-color: white; color: white;")##
            # self.maximize_icon.setStyleSheet("background-color: white; color: white;")##
            self.maximize_button.clicked.connect(self.maxmizeWindow)
            layout.addWidget(self.maximize_button)
            
            close_button = QPushButton()
            close_icon = QIcon(GraphicsDirectoryPath('Close (1).png'))
            close_button.setIcon(close_icon)
            close_button.setStyleSheet("background-color:white")
            close_button.clicked.connect(self.closeWindow)
            layout.addWidget(close_button)
            
            line_frame = QFrame()
            line_frame.setFixedHeight(1)
            line_frame.setFrameShape(QFrame.HLine)
            line_frame.setFrameShadow(QFrame.Sunken)
            line_frame.setStyleSheet("border-color: black;")
            title_label = QLabel(f" {str(Assistantname).capitalize()} AI    ")
            title_label.setStyleSheet("color: black; font-size: 18px ;; background-color:white")
            home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
            message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
            layout.addWidget(title_label)
            layout.addStretch(1)
            layout.addWidget(home_button)
            layout.addWidget(message_button)
            layout.addStretch(1)
            layout.addWidget(minimize_button)
            layout.addWidget(self.maximize_button)
            layout.addWidget(close_button)
            layout.addWidget(line_frame)
            self.draggable = True
            self.offset = None
            
    def printEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.white)
            super().paintEvent(event)
            
    def minimizeWindow(self):
            self.parent.showMinimized()
    
    def maxmizeWindow(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent.showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
   
    def closeWindow(self):
        self.parent.close()
    
    def mousePressEvent(self, event):
        if self.draggable:
                self.offset = event.pos()    
                
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos()- self.offset
            self.parent().move(new_pos)
            
    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
            
        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen
        
    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()
            
        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen
        
class MainWindow(QMainWindow):

    def __init__ (self):
        super() .__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    GraphicalUserInterface()