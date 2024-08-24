# Import necessary libraries
import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
from pynput.keyboard import Controller
import cvzone
import numpy as np
import pygame

# Initialize sound effects
pygame.mixer.init()
click_sound = pygame.mixer.Sound('c:\\Users\\ps484\\Downloads\\157766__enok123__keyboard-click.wav')
hover_sound = pygame.mixer.Sound('c:\\Users\\ps484\\Downloads\\701742__perduuus__uibuttonhover.wav')

# Set up video capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # Set width
cap.set(4, 720)   # Set height

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

# Define keyboard layout
keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["Sp", "En", "Ba", "Cl"]
]

# Initialize variables
finalText = ""
Keyboard = Controller()

# Function to draw the keyboard on the image
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        
        # Draw button outline and fill color based on hover state
        cvzone.cornerRect(img, (x, y, w, h), 20, rt=0)
        color = (0, 150, 0) if button.hover else (150, 0, 0)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
        
        # Draw button text
        font_scale = min(button.size) / 40
        thickness = int(font_scale * 2)
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, font_scale, thickness)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(img, button.text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), thickness)
    return img

# Function to display the help screen
def display_help_screen(img):
    help_text = [
        "Enjoy your experience with your own virtual Keyboard.",
        "Built by - Pratyush Singh",
        "Dated - 24-08-2024",
        "Virtual Keyboard Help",
        "1. Hover over a key with your hand to highlight it.",
        "2. Pinch to press a key.",
        "3. Special keys:",
        "   - Space: Adds a space",
        "   - Enter: Adds a new line",
        "   - Backspace: Deletes the last character",
        "   - Clear: Clears the text",
        "Press 'H' to hide this help screen."
    ]
    
    # Draw semi-transparent background and help text
    cv2.rectangle(img, (50, 50), (1230, 670), (0, 0, 0), cv2.FILLED)
    cv2.addWeighted(img, 0.5, img, 0.5, 0, img)
    for i, line in enumerate(help_text):
        cv2.putText(img, line, (60, 100 + i * 40), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

# Button class for keyboard keys
class Buttons():
    def __init__(self, pos, text, size=(70, 70)):
        self.pos = pos
        self.size = size
        self.text = text
        self.hover = False

# Create buttons based on keyboard layout
buttonList = []
for i, row in enumerate(keys):
    for x, key in enumerate(row):
        size = (140, 70) if key in ["Sp", "En", "Ba", "Cl"] else (70, 70)
        buttonList.append(Buttons([100 * x + 20, 100 * i + 20], key, size))

# Initialize help screen state
last_hovered_button = None
help_screen_active = False

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    hands, img = detector.findHands(img)
    
    if help_screen_active:
        display_help_screen(img)
    else:
        img = drawAll(img, buttonList)

        if hands:
            hand1 = hands[0]
            lmList = hand1["lmList"]

            hovered_button = None

            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    button.hover = True
                    hovered_button = button
                    cv2.rectangle(img, (x-5, y-5), (x + w + 5, y + h + 5), (255, 0, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 50), cv2.FONT_HERSHEY_PLAIN, 3, (150, 150, 150), 4)

                    # Check for pinch gesture
                    if len(lmList) > 12:
                        x1, y1 = lmList[8][0], lmList[8][1]
                        x2, y2 = lmList[12][0], lmList[12][1]
                        l, _, _ = detector.findDistance((x1, y1), (x2, y2), img)

                        # Perform action based on button text
                        if l < 40:
                            if button.text == "Cl":
                                finalText = ""
                            elif button.text == "Sp":
                                finalText += " "
                            elif button.text == "En":
                                finalText += "\n"
                            elif button.text == "Ba":
                                finalText = finalText[:-1]
                            else:
                                Keyboard.press(button.text)
                                finalText += button.text
                            
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            cv2.putText(img, button.text, (x + 15, y + 60), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
                            click_sound.play()
                            sleep(0.20)
                else:
                    button.hover = False

            if hovered_button and hovered_button != last_hovered_button:
                hover_sound.play()

            last_hovered_button = hovered_button
        
        # Display the typed text
        cv2.rectangle(img, (50, 700), (1230, 600), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, finalText, (60, 675), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break  # Exit the loop
    elif key == ord('h'):
        help_screen_active = not help_screen_active  # Toggle help screen