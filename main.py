from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from sklearn.cluster import KMeans
import uvicorn

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_colors(image, n_colors=5):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = img.reshape((-1, 3))
    kmeans = KMeans(n_clusters=n_colors, random_state=42)
    kmeans.fit(img)
    colors = kmeans.cluster_centers_.astype(int)
    return colors.tolist()

@app.post("/analyze")
async def analyze_room(file: UploadFile = File(...)):
    contents = await file.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        return JSONResponse(content={"error": "Invalid image"}, status_code=400)

    colors = extract_colors(img)
    recommendations = [
        {"style": "Scandinavian", "match": "85%", "description": "Bright tones & natural wood"},
        {"style": "Minimalist", "match": "78%", "description": "Clean lines, neutral colors"},
        {"style": "Industrial", "match": "65%", "description": "Exposed brick, rustic decor"}
    ]

    return {"dominant_colors": colors, "recommendations": recommendations}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
