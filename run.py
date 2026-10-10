import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("🚀 Server starting at: http://localhost:8000/")
    print("Open this URL in your browser to use the tool.")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
