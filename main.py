import tensorflow as tf
import numpy as np
from PIL import Image
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from io import BytesIO
import uvicorn

# Load the pre-trained model
MODEL = tf.keras.models.load_model("mohit.h5")
CLASS_NAMES = ["fakenotes", "realNotes"]

# Initialize the FastAPI app
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3001",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("static/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/ping")
async def ping():
    return "Hello, I am alive"

def read_file_as_image(data) -> np.ndarray:
    try:
        image = Image.open(BytesIO(data)).convert("RGB")
        expected_shape = MODEL.input_shape[1:3]
        image = image.resize(expected_shape)
        image = np.array(image).astype("float32")
        image = image / 255.0
        return image
    except Exception as e:
        raise ValueError("Error processing the image") from e

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image = read_file_as_image(await file.read())
        img_batch = np.expand_dims(image, axis=0)

        predictions = MODEL.predict(img_batch)

        # Apply temperature scaling
        temperature = 0.01
        exp_preds = np.exp(predictions[0] / temperature)
        scaled_predictions = exp_preds / np.sum(exp_preds)

        predicted_class = CLASS_NAMES[np.argmax(scaled_predictions)]
        confidence = np.max(scaled_predictions)  # Replacing confidence with accuracy

        return {
            'class': predicted_class,
            'confidence': float(confidence * 100)  # Return percentage
        }
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8001)
