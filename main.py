from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from processor import process_image

app = FastAPI(title="Handwriting Synthesizer API")

@app.get("/")
def read_root():
    return {"message": "Handwriting Synthesizer API is running!"}

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드 받아 텍스트를 지우고 폰트를 합성하여 반환합니다.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    image_bytes = await file.read()
    
    try:
        # 이미지 처리 파이프라인 실행
        result_bytes = process_image(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")
