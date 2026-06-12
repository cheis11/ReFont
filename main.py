from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from processor import process_image

app = FastAPI(title="Handwriting Synthesizer API")

# 프론트엔드 연동을 위한 CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Handwriting Synthesizer API is running!"}

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드 받아 텍스트를 추출하고 손글씨로 렌더링하여 반환합니다.
    """
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    image_bytes = await file.read()
    
    try:
        # 이미지 처리 파이프라인 실행
        result_bytes = process_image(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
