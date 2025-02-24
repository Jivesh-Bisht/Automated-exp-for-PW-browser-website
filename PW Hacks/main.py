import cv2
import pyautogui
import json
import time
import os
import numpy as np

time.sleep(3)

# Load answers from JSON file
with open("answers.json", "r", encoding="utf-8") as f:
    answers = json.load(f)

# Directory containing question images
QUESTIONS_DIR = "questions"

# Load all question images
question_images = {img: cv2.imread(os.path.join(QUESTIONS_DIR, img), 0) for img in os.listdir(QUESTIONS_DIR)}

# Load input field image for integer-type questions
input_field_img = cv2.imread("input_field.png", 0)

# Load button images
submit_question_img = cv2.imread("submit_question.png", 0)
next_button_img = cv2.imread("next.png", 0)
final_submit_img = cv2.imread("submit.png", 0)
yes_button_img = cv2.imread("yes.png", 0)
skip_button_img = cv2.imread("skip.png", 0)
reattempt_button_img = cv2.imread("reattempt.png", 0)

# Function to find an image on the screen
def find_image_on_screen(image, threshold=0.5):
    screen = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)
    
    result = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        return max_loc  # Return top-left corner coordinates
    return None

# Function to click at a location
def click_at(x, y):
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()

# Function to enter text
def enter_text(text):
    pyautogui.write(str(text), interval=0.05)

# Main loop for answering questions
while True:
    question_count = 0
    while question_count < 10:
        print(f"Processing Question {question_count + 1}...")

        # Find which question is on the screen
        matched_question = None
        for filename, question_img in question_images.items():
            loc = find_image_on_screen(question_img)
            if loc:
                matched_question = filename
                break

        if not matched_question:
            print("No matching question found on screen.")
            continue

        print(f"Matched: {matched_question}")
        
        # Extract question number from filename (e.g., "q3.png" → "q3")
        question_key = matched_question.split(".")[0]
        if question_key not in answers:
            print(f"No answer found for {question_key}. Skipping...")
            continue

        correct_answer = answers[question_key]
        print(f"Correct answer: {correct_answer}")

        # Check if the question is integer-type
        if isinstance(correct_answer, int):
            print("Detected integer-type question.")

            # Find input field
            input_field_location = find_image_on_screen(input_field_img)

            if input_field_location:
                print("Clicking on input field...")
                click_at(input_field_location[0] + 10, input_field_location[1] + 10)
                time.sleep(0.1)
                
                # Enter integer answer
                print(f"Entering answer: {correct_answer}")
                enter_text(correct_answer)

        else:
            # Multiple-choice question
            question_location = find_image_on_screen(question_img)
            if question_location:
                question_x, question_y = question_location  # Get question coordinates

                # Keep searching for the correct option below the question
                while True:
                    option_img = cv2.imread(f"options/{correct_answer}.png", 0)
                    option_location = find_image_on_screen(option_img, threshold=0.75)

                    if option_location:
                        option_x, option_y = option_location  # Get option coordinates

                        # Ensure the option is BELOW the question
                        if option_y > question_y:
                            print(f"Clicking on option {correct_answer.upper()} at ({option_x}, {option_y})")
                            click_at(option_x + 10, option_y + 10)
                            break  # Exit loop once the correct option is found
                        else:
                            print(f"Skipping incorrect match for {correct_answer.upper()} (too high on screen)")

        # Search for "Submit Question" button and click it
        submit_location = find_image_on_screen(submit_question_img)
        
        if submit_location:
            print("Clicking 'Submit Question' button...")
            click_at(submit_location[0] + 10, submit_location[1] + 10)

        # Search for "Next" button and click it
        time.sleep(.1)  # Small delay before searching for the next button
        next_location = find_image_on_screen(next_button_img)
        
        if next_location:
            print("Clicking 'Next' button...")
            click_at(next_location[0] + 10, next_location[1] + 10)

        question_count += 1
        time.sleep(0.1)

    # Click the final "Submit" button after 10 questions
    submit_final_location = find_image_on_screen(final_submit_img)
    if submit_final_location:
        print("Clicking final 'Submit' button...")
        click_at(submit_final_location[0] + 10, submit_final_location[1] + 10)

    time.sleep(0.1)  # Wait for confirmation popup

    # Click "Yes" to confirm final submission
    yes_location = find_image_on_screen(yes_button_img)
    if yes_location:
        print("Clicking 'Yes' button...")
        click_at(yes_location[0] + 10, yes_location[1] + 10)

    time.sleep(0.1)  # Wait for next screen

    # Click "Skip" button
    skip_location = find_image_on_screen(skip_button_img)
    if skip_location:
        print("Clicking 'Skip' button...")
        click_at(skip_location[0] + 10, skip_location[1] + 10)

    time.sleep(0.3)  # Wait before reattempt

    # Click "Reattempt" button
    reattempt_location = find_image_on_screen(reattempt_button_img)
    if reattempt_location:
        print("Clicking 'Reattempt' button...")
        click_at(reattempt_location[0] + 10, reattempt_location[1] + 10)

    time.sleep(0.5)  # Short delay before restarting the loop
