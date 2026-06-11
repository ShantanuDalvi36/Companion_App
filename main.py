import sys
import time
from threading import Thread
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
import win32gui 
from pynput import keyboard, mouse


class FrierenCompanion(QWidget):

 # Initialize variables, UI, listeners, and timers
   def __init__(self):
        super().__init__()
        self.current_state = "IDLE"

    # mouse event
        self.last_keypress_time = 0
        self.drag_position = None
        self.last_activity_time = time.time()
        self.is_dragging = False
        self.wake_up_until = 0
        self.last_petting_movement = 0
        self.start_mouse_listener()

        self.normal_width = 180
        self.normal_height = 180

        self.setup_ui()

        self.resize(self.normal_width, self.normal_height)
        self.show()

        self.move_to_taskbar_position()

        self.start_keyboard_listener()
        

        self.active_app = "OTHER"
        self.active_tab = ""
        self.last_tab = ""

        self.last_petting_movement = 0

        self.app_keywords = {
            "youtube": "WATCHING",
            "chatgpt": "AI",
            "github": "CODING",
            "leetcode": "STUDYING",
            "stackoverflow": "CODING",
            "vscode": "CODING",
            "visual studio code": "CODING",
            "discord": "CHAT",
            "spotify": "MUSIC",
            "root/Shell":"CODING"
        }
        
        self.idle_images = [
        "assets/frieren.png",
        "assets/frieren.png",
        "assets/frieren.png",
        "assets/idle1.png",
        "assets/idle2.png",
        "assets/idle3.png"
        ]

        self.coding_images = [
            "assets/fri_writting.png"
        ]

        self.ai_images = [
            "assets/fri_wake_up.png"
        ]

        self.watching_images = [
            "assets/frieren.png"
        ]

        self.chat_images = [
            "assets/fri_dragging.png"
        ]

        self.is_hovering = False
        self.last_hover_move = 0
        self.petting_started = False

        self.last_idle_switch = time.time()
        self.idle_switch_interval = random.randint(30, 45)  # seconds
        self.visual_lock = False

        self.coding_dialogues = [
            "More coding?",
            "Try not to create bugs.",
            "Another project?",
            "Back to work."
        ]

        self.ai_dialogues = [
            "Researching something?",
            "Interesting...",
            "Asking ChatGPT again?",
            "Learning something new?"
        ]

        self.watching_dialogues = [
            "Taking a break?",
            "Watching videos?",
            "Looks relaxing."
        ]

        self.chat_dialogues = [
            "Talking with someone?",
            "Busy conversation?",
            "Hope it's important."
        ]
        self.last_dialogue_time = 0
        self.dialogue_cooldown = 30

        QTimer.singleShot(0, self.play_entry_animation)

# Create the companion window and widgets
   def setup_ui(self):

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        layout = QVBoxLayout()

        self.image_label = QLabel()
        pixmap = QPixmap("assets/frieren.png")
        pixmap = pixmap.scaled(
            self.normal_width,
            self.normal_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

        self.dialogue_label = QLabel("")

        self.dialogue_label.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.dialogue_label.setStyleSheet("""
                QLabel {
                    background-color: #6B89A8;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 12px 20px;
                    font-size: 12pt;
                }
            """)

        self.dot1 = QLabel("")
        self.dot2 = QLabel("")
        self.dot3 = QLabel("")

        for dot in [self.dot1, self.dot2, self.dot3]:
            dot.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool
            )


        self.dot1.setFixedSize(14, 14)
        self.dot2.setFixedSize(10, 10)
        self.dot3.setFixedSize(6, 6)

        self.dot1.setStyleSheet("""
        background-color: #6B89A8;
        border-radius: 7px;
        """)

        self.dot2.setStyleSheet("""
        background-color: #6B89A8;
        border-radius: 5px;
        """)

        self.dot3.setStyleSheet("""
        background-color: #6B89A8;
        border-radius: 3px;
        """)

        self.dialogue_label.setMaximumWidth(250)
        self.dialogue_label.setWordWrap(True)

        self.dot1.hide()
        self.dot2.hide()
        self.dot3.hide()

        self.dialogue_label.hide()
        
        self.state_label = QLabel("State: IDLE")
        self.state_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            background-color: rgba(0,0,0,120);
            padding: 5px;
        """)

        layout.addWidget(self.image_label)
        layout.addWidget(self.state_label)

        self.setLayout(layout)

        self.move(100, 100)

        self.original_geometry = self.geometry()

# show Dialogue 
   def app_reaction(self):

    current_time = time.time()

    if current_time - self.last_dialogue_time < self.dialogue_cooldown:
        return

    import random

    if self.active_app == "CODING":

        self.show_dialogue(
            random.choice(self.coding_dialogues)
        )

    elif self.active_app == "AI":

        self.show_dialogue(
            random.choice(self.ai_dialogues)
        )

    elif self.active_app == "WATCHING":

        self.show_dialogue(
            random.choice(self.watching_dialogues)
        )

    elif self.active_app == "CHAT":

        self.show_dialogue(
            random.choice(self.chat_dialogues)
        )

    self.last_dialogue_time = current_time
# Dialogue box 
   def show_dialogue(self, text):

    self.dialogue_label.setText(text)
    self.dialogue_label.adjustSize()

    companion_x = self.x()
    companion_y = self.y()

    bubble_x = (
        companion_x
        + self.width() // 2
        - self.dialogue_label.width() // 2
        -80
    )

    bubble_y = (
        companion_y
        - self.dialogue_label.height()
        + 10
    )

    self.dialogue_label.move(
        bubble_x,
        bubble_y
    )

    self.dot1.move(
        bubble_x + 45,
        bubble_y + self.dialogue_label.height() - 2
    )

    self.dot2.move(
        bubble_x + 60,
        bubble_y + self.dialogue_label.height() + 12
    )

    self.dot3.move(
        bubble_x + 72,
        bubble_y + self.dialogue_label.height() + 24
    )

    self.dialogue_label.show()

    self.dot1.show()
    self.dot2.show()
    self.dot3.show()

    QTimer.singleShot(
        3000,
        self.hide_dialogue
    )

# Hide dialogue box
   def hide_dialogue(self):

        self.dialogue_label.hide()

        self.dot1.hide()
        self.dot2.hide()
        self.dot3.hide()

# Handle mouse click and start dragging
   def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.last_activity_time = time.time()

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

        event.accept()

# Move the companion while dragging
   def mouseMoveEvent(self, event):

        print("Mouse moving on companion")

        if self.drag_position is not None:

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )
        
            event.accept()

            self.last_activity_time = time.time()
        
        if not self.is_dragging:

            self.last_hover_move = time.time()
            self.last_petting_movement = time.time()
   
        if self.current_state == "SLEEPING":
            self.wake_up_until = time.time() + 2
    
# Stop dragging when mouse button is released
   def mouseReleaseEvent(self, event):

            self.drag_position = None

            self.is_dragging = False
            self.last_activity_time = time.time()
            self.update_state()

# Detect global mouse movement
   def on_mouse_move(self, x, y):

        if not self.is_dragging:
            self.last_hover_move = time.time()
   
        self.last_activity_time = time.time()

        if self.current_state == "SLEEPING":
            self.wake_up_until = time.time() + 2

# Start a background mouse listener
   def start_mouse_listener(self):

        listener = mouse.Listener(
            on_move=self.on_mouse_move
        )

        listener.daemon = True
        listener.start()

   def enterEvent(self, event):

        self.is_hovering = True
        self.last_hover_move = time.time()
        self.hover_start_time = time.time()
    
   def leaveEvent(self, event):

        self.is_hovering = False
        self.petting_started = False

        if self.current_state == "PETTING":
            self.change_state("IDLE")

    

# Start listening for keyboard input
   def start_keyboard_listener(self):

        listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        listener.daemon = True
        listener.start()

# checks what windows are active 
   def get_active_window(self):

        window = win32gui.GetForegroundWindow()

        return win32gui.GetWindowText(window)
   
# checks for active apps and tabs
   def check_active_app(self):

        title = self.get_active_window()
        print(title)

   def check_active_app(self):

        title = self.get_active_window()

        if title != self.last_tab:

            self.active_tab = title
            self.last_tab = title

            print(f"Tab: {title}")

        lower_title = title.lower()

        detected_app = "OTHER"

        for keyword, app_type in self.app_keywords.items():

            if keyword in lower_title:

                detected_app = app_type
                break

        if detected_app != self.active_app:

            self.active_app = detected_app

            print(f"Activity: {self.active_app}")

            self.app_reaction()
        
      
# Start timer that checks and updates states
   def start_state_checker(self):

        print("STATE CHECKER STARTED")
        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_state
        )
        #check for idle state
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self.handle_idle_animation)
        self.idle_timer.start(3000)
        
        #checks for petting state
        self.pet_timer = QTimer()
        self.pet_timer.timeout.connect(self.check_petting)
        self.pet_timer.start(100)

        #checks for active windows(apps)
        self.app_timer = QTimer()
        self.app_timer.timeout.connect(self.check_active_app)
        self.app_timer.start(2000)

        self.timer.start(100)

# Determine and update the current companion state
   def update_state(self):

        if self.current_state == "LEAVING":
            return

        current_time = time.time()

        if self.is_dragging:
            new_state = "DRAGGING"

        elif current_time < self.wake_up_until:
            new_state = "WAKE_UP"

        elif current_time - self.last_activity_time > 240:
            new_state = "SLEEPING"

        elif current_time - self.last_keypress_time < 3:
            new_state = "TYPING"

        else:
            new_state = "IDLE"

        if new_state != self.current_state:

            print(f"{self.current_state} -> {new_state}")

            self.change_state(new_state)

# checks whether mouse is in pettable area       
   def check_petting(self):

        current_time = time.time()

        if self.is_hovering:

            if current_time - self.hover_start_time > 1:

                if current_time - self.last_hover_move < 1:

                    if self.current_state != "PETTING":

                        self.change_state("PETTING")

                    self.last_petting_movement = current_time

        if self.current_state == "PETTING":

            if current_time - self.last_petting_movement > 0.5:

                self.change_state("IDLE")

# Record keyboard activity
   def on_key_press(self, key):

        now = time.time()

        self.last_keypress_time = now
        self.last_activity_time = now

        if self.current_state == "SLEEPING":
            self.wake_up_until = now + 2
        
        if self.current_state != "TYPING":
            self.change_state("TYPING")
    
# Show entry animation 
   def play_entry_animation(self):

        self.setGeometry(self.centered_geometry(10, 10))

        self.entry_anim = QPropertyAnimation(self, b"geometry")
        self.entry_anim.setDuration(500)

        self.entry_anim.setStartValue(self.geometry())

        self.entry_anim.setEndValue(
            self.centered_geometry(self.normal_width, self.normal_height)
        )

        self.entry_anim.start()
        self.entry_anim.finished.connect(self.enable_state_machine)

# starts state machine after entry animation
   def enable_state_machine(self):

        print("ENTRY FINISHED")
        self.show_dialogue("Hello.")

        self.start_state_checker()

    # Show leave animation before exiting   
   def close_with_animation(self):

        self.change_state("LEAVING")

        QTimer.singleShot(
            800,
            self.zoom_out_and_close
        )

# Play zoom-out animation and close application
   def zoom_out_and_close(self):

        self.exit_anim = QPropertyAnimation(self, b"geometry")
        self.exit_anim.setDuration(500)

        self.exit_anim.setStartValue(self.geometry())

        self.exit_anim.setEndValue(
            self.centered_geometry(10, 10)
        )

        self.exit_anim.finished.connect(
            QApplication.instance().quit
        )

        self.exit_anim.start()

# helper function maintains center of the frame
   def centered_geometry(self, width, height):

        current = self.geometry()
        center = current.center()

        return QRect(
            center.x() - width // 2,
            center.y() - height // 2,
            width,
            height
        )

# Display right-click context menu
   def contextMenuEvent(self, event):

        menu = QMenu(self)

        settings_action = menu.addAction("Settings")
        hide_action = menu.addAction("Hide")
        exit_action = menu.addAction("Exit")

        action = menu.exec(event.globalPos())

        if action == settings_action:
            print("Settings clicked")

        elif action == hide_action:
            self.hide()

        elif action == exit_action:
            self.close_with_animation()
        
 # Change the displayed character image
   def set_character_image(self, image_path):

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"ERROR: Could not load {image_path}")
            return

        pixmap = pixmap.scaled(
            self.normal_width,
            self.normal_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

# Moves frieren to bottom right on top of taskbar
   def move_to_taskbar_position(self):

        screen = QGuiApplication.primaryScreen().geometry()

        x = screen.width() - self.normal_width - 110
        y = screen.height() - self.normal_height - 185

        self.move(x, y)

# Handles indle state random animations
   def handle_idle_animation(self):

    if self.current_state != "IDLE":
        return

    if self.visual_lock:
        return

    current_time = time.time()

    if current_time - self.last_idle_switch > self.idle_switch_interval:

        if self.active_app == "CODING":

            image = random.choice(self.coding_images)

        elif self.active_app == "AI":

            image = random.choice(self.ai_images)

        elif self.active_app == "WATCHING":

            image = random.choice(self.watching_images)

        elif self.active_app == "CHAT":

            image = random.choice(self.chat_images)

        else:

            image = random.choice(self.idle_images)

        self.set_character_image(image)

        self.last_idle_switch = current_time

        self.idle_switch_interval = random.randint(30, 45)

       

# Update state and corresponding character image 
   def change_state(self, new_state):

        self.current_state = new_state
        self.state_label.setText(f"State: {new_state}")

        # LOCK prevents idle timer from overriding visuals
        self.visual_lock = True

        if new_state == "TYPING":
            self.set_character_image("assets/fri_writting.png")

        elif new_state == "SLEEPING":
            self.set_character_image("assets/fri_sleeping.png")

        elif new_state == "DRAGGING":
            self.set_character_image("assets/fri_dragging.png")

        elif new_state == "WAKE_UP":
            self.set_character_image("assets/fri_wake_up.png")

        elif new_state == "LEAVING":
            self.set_character_image("assets/fri_leaving.png")
        
        elif new_state == "PETTING":
            self.set_character_image("assets/fri_petting.png")

        elif new_state == "IDLE":
            self.set_character_image("assets/frieren.png")

            self.last_idle_switch = time.time()
            self.idle_switch_interval = random.randint(15, 30)

        # unlock after short delay
        QTimer.singleShot(300, self.unlock_visual)

   def unlock_visual(self):
        self.visual_lock = False

# Main method       
if __name__ == "__main__":

    app = QApplication(sys.argv)

    companion = FrierenCompanion()
    companion.show()

    sys.exit(app.exec())