# WakeyWakey
WakeyWakey is a windows study monitor app that screams "Faaaah!" when it detects  dosing via webcam so that you cant get back yo studying!


Project Overview
WakeyWakey is a lightweight, background-monitored study aid designed to keep you alert during intense study sessions. By utilizing real-time computer vision, the application monitors your face and eyes to trigger an audible alarm if it detects you have been closing your eyes for an extended period.

Core Functionality
Real-time Eye-State Analysis: Leverages OpenCV and Haar Cascades for efficient and responsive facial feature detection.

Stealth Monitoring: Runs silently in the background, allowing you to maintain focus without an intrusive or distracting camera feed.

Customizable Alerts: Provides a reliable alarm system that triggers only after a user-defined threshold of drowsiness, using native Windows audio integration.

Intuitive Control: Features a clean, user-friendly GUI built with Tkinter for easy start/stop management.

Getting Started
Dependencies: The application requires Python 3.x and the opencv-python library.

Deployment: The project is designed for portability and can be compiled into a standalone Windows executable (.exe) using PyInstaller, making it easy to share or run on different workstations.

Usage: Simply launch the application, ensure your webcam has adequate lighting to avoid backlighting issues, and toggle the tracking status via the control panel.

Project Attribution
This application was created to assist with maintaining high levels of focus and productivity during demanding academic or professional tasks.

Developed by: praise 🩷
