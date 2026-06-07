import sys
import time
from threading import Thread

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect

from pynput import keyboard, mouse


class FrierenCompanion(QWidget):

    def __init__(self):
        super().__init__()

        self.last_keypress_time = 0
        self.current_state = "IDLE"
        self.drag_position = None
        self.setup_ui()
        self.start_keyboard_listener()
        self.start_state_checker()
        self.start_mouse_listener()
        self.last_activity_time = time.time()
        self.is_dragging = False
        self.wake_up_until = 0

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.last_activity_time = time.time()

            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

        event.accept()

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
    
    def mouseReleaseEvent(self, event):

            self.drag_position = None

            self.is_dragging = False
            self.last_activity_time = time.time()
        
    def on_mouse_move(self, x, y):

        self.last_activity_time = time.time()

        if self.current_state == "SLEEPING":
            self.wake_up_until = time.time() + 2
    
    def start_mouse_listener(self):

        listener = mouse.Listener(
            on_move=self.on_mouse_move
        )

        listener.daemon = True
        listener.start()
    


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

        self.original_geometry = self.geometry()
   


    def start_keyboard_listener(self):

        listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        listener.daemon = True
        listener.start()

    def start_state_checker(self):

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_state
        )

        self.timer.start(500)

    def update_state(self):

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
            
            self.change_state(new_state)

            if new_state != self.current_state:

                self.current_state = new_state

                print("State:", self.current_state)

                self.state_label.setText(
                    f"State: {self.current_state}"

            
            )

    def on_key_press(self, key):

        now = time.time()

        self.last_keypress_time = now
        self.last_activity_time = now

        if self.current_state == "SLEEPING":
            self.wake_up_until = now + 2
    

    def zoom_out_and_close(self):

            print("Zooming out")

            current = self.geometry()

            center_x = current.center().x()
            center_y = current.center().y()

            self.exit_animation = QPropertyAnimation(
                self,
                b"geometry"
            )

            self.exit_animation.setDuration(700)

            self.exit_animation.setStartValue(current)

            self.exit_animation.setEndValue(
                QRect(
                    center_x,
                    center_y,
                    0,
                    0
                )
            )

            self.exit_animation.finished.connect(
                QApplication.instance().quit
            )

            self.exit_animation.start()
        
    
    def close_with_animation(self):

        print("Playing leave animation")

        self.set_character_image(
            "assets/fri_leaving.png"
        )

        QTimer.singleShot(
            1500,
            self.zoom_out_and_close
        )

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
        
if __name__ == "__main__":

    app = QApplication(sys.argv)

    companion = FrierenCompanion()
    companion.show()

    sys.exit(app.exec())