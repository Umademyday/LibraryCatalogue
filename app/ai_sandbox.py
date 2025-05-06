import cv2
import pytesseract
# from PIL import Image
# import re


def preprocess_image(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # reduce noise
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh


def extract_text(image):
    return pytesseract.image_to_string(image)


if __name__ == "__main__":
    image_path = "covers/cover1.jpg"
    preprocessed = preprocess_image(image_path)
    text = extract_text(preprocessed)

    print("\n--- Raw OCR Text ---\n", text)

