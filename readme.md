# Frieren Desktop Companion

A desktop companion inspired by Frieren built using Python and PyQt6.

## Features

* Draggable desktop companion
* Typing detection
* Idle state detection
* Sleep state after inactivity
* Wake-up state on user interaction
* Right-click context menu
* Custom character sprites
* Always-on-top companion window

## Tech Stack

* Python
* PyQt6
* pynput

## Project Structure

```
Companion_App/
│
├── main.py
├── assets/
│   ├── frieren.png
│   ├── fri_leaving.png
│   └── ...
│
├── .gitignore
└── README.md
```

## Future Plans

* Character animations
* Settings window
* System tray integration
* Multiple character states
* Sound effects
* Custom themes
* Additional companions

## Run Locally

Install dependencies:

```bash
pip install PyQt6 pynput
```

Run the application:

```bash
python main.py
```
