"""
Simple script to run the FastAPI server.
Run this to start the API server.
"""
import uvicorn
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 70)
    print("Starting Football Predictor FastAPI Server")
    print("=" * 70)
    print("\nServer will be available at:")
    print("  - API: http://127.0.0.1:8001")
    print("  - Docs: http://127.0.0.1:8001/docs")
    print("  - Health: http://127.0.0.1:8001/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        uvicorn.run(
            "fastapi_predictor:app",
            host="127.0.0.1",
            port=8001,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

