import pytesseract
from PIL import Image

img = Image.open('captcha.png')
pytesseract.pytesseract.tesseract_cmd = r'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'
print(pytesseract.image_to_string(img).strip())