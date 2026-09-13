import uvicorn
import sys
from backend.app.config import DEVICE, CUDA_AVAILABLE, GPU_NAME, APP_NAME

if __name__ == "__main__":
    print("=" * 70)
    print(f"Starting {APP_NAME}")
    print(f"Hardware Accelerator: {DEVICE} ({GPU_NAME})")
    print("Zero-Watermark Human-Authored Architecture")
    print("Web Gateway: http://127.0.0.1:8000")
    print("=" * 70)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False, workers=1)
