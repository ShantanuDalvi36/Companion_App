import sys
import time
from threading import Thread

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PyQt6.QtGui import QPixmap, QGuiApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect

from pynput import keyboard, mouse


class FrierenCompanion(QWidget):

 # Initialize variables, UI, listeners, and timers
   def __init__(self):
    super().__init__()

    self.last_keypress_time = 0
    self.current_state = "IDLE"
    self.drag_position = None

    self.last_activity_time = time.time()
    self.is_dragging = False
    self.wake_up_until = 0

    self.normal_width = 250
    self.normal_height = 250

    self.setup_ui()

    self.resize(self.normal_width, self.normal_height)
    self.show()

    self.move_to_taskbar_position()

    self.start_keyboard_listener()
    self.start_mouse_listener()

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
            250,
            250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)
        
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

        self.normal_width = 250
        self.normal_height = 250

        self.original_geometry = self.geometry()


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

        if self.drag_position is not None:

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()

            self.last_activity_time = time.time()

        if self.current_state == "SLEEPING":
            self.wake_up_until = time.time() + 2
    
# Stop dragging when mouse button is released
   def mouseReleaseEvent(self, event):

            self.drag_position = None

            self.is_dragging = False
            self.last_activity_time = time.time()

# Detect global mouse movement
   def on_mouse_move(self, x, y):

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
    

# Start listening for keyboard input
   def start_keyboard_listener(self):

        listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        listener.daemon = True
        listener.start()

# Start timer that checks and updates states
   def start_state_checker(self):

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_state
        )

        self.timer.start(500)

# Determine and update the current companion state
   def update_state(self):

        if self.current_state == "LEAVING":
            return

        current_time = time.time()

        if self.is_dragging:
            new_state = "DRAGGING"

        elif current_time < self.wake_up_until:
            new_state = "WAKE_UP"

        elif current_time - self.last_activity_time > 10:
            new_state = "SLEEPING"

        elif current_time - self.last_keypress_time < 2:
            new_state = "TYPING"

        else:
            new_state = "IDLE"

        if new_state != self.current_state:
            self.change_state(new_state)

# Record keyboard activity
   def on_key_press(self, key):

        now = time.time()

        self.last_keypress_time = now
        self.last_activity_time = now

        if self.current_state == "SLEEPING":
            self.wake_up_until = now + 2
    
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
            250,
            250,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

# Moves frieren to bottom right on top of taskbar
   def move_to_taskbar_position(self):

        screen = QGuiApplication.primaryScreen().geometry()

        taskbar_height = 60  # approximate (works for most Windows setups)

        x = screen.width() - self.normal_width - 150
        y = screen.height() - self.normal_height - 213

        self.move(x, y)

# Update state and corresponding character image 
   def change_state(self, new_state):

        self.current_state = new_state

        self.state_label.setText(
            f"State: {new_state}"
        )

        if new_state == "IDLE":
            self.set_character_image(
                "assets/frieren.png"
            )

        elif new_state == "TYPING":
            self.set_character_image(
                "assets/fri_writting.png"
            )

        elif new_state == "SLEEPING":
            self.set_character_image(
                "assets/fri_sleeping.png"
            )
        
        elif new_state == "DRAGGING":
            self.set_character_image(
                "assets/fri_dragging.png"
            )
        
        elif new_state == "WAKE_UP":
            self.set_character_image(
                "assets/fri_wake_up.png"
            )

        elif new_state == "LEAVING":
            self.set_character_image(
                "assets/fri_leaving.png"
            )

# Main method       
if __name__ == "__main__":

    app = QApplication(sys.argv)

    companion = FrierenCompanion()
    companion.show()

    sys.exit(app.exec())