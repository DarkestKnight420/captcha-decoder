from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import pytesseract
import base64
from PIL import Image
import io


app = FastAPI()


class ImageData(BaseModel):
    image_base64: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/solve-captcha")
async def solve_captcha(data: ImageData):
    # Decode the base64 string to bytes
    try:
        img_bytes = base64.b64decode(data.image_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 string: {e}")

    img = Image.open(io.BytesIO(img_bytes))

    # If the image is a GIF, convert it to JPEG
    if img.format == 'GIF':
        with io.BytesIO() as output:
            img.convert('RGB').save(output, format='JPEG')
            img_bytes = output.getvalue()

    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    captcha_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if captcha_image is None:
        raise HTTPException(status_code=500, detail="Failed to decode the image.")

    # Process the image
    gray = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(dilated, config=custom_config)

    return {"answer": text.strip()}
