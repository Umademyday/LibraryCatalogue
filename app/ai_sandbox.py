import cv2
import pytesseract


def preprocess_image(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # reduce noise
    _, thresh = cv2.threshold(gray, 60, 250, cv2.THRESH_BINARY)
    return thresh


def extract_text(image):
    return pytesseract.image_to_string(image, lang='eng+esp+rus')


if __name__ == "__main__":
    image_path = "covers/cover4.jpg"
    preprocessed = preprocess_image(image_path)
    cv2.imshow("Processed Image", preprocessed)
    cv2.waitKey(0)  # Wait until a key is pressed
    cv2.destroyAllWindows()
    text = extract_text(preprocessed)

    print("\n--- Raw OCR Text ---\n", text)

