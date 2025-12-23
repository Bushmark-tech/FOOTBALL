"""
Production startup script for FastAPI server.
Optimized for millions of users with proper worker configuration.
"""
import os
import sys
import subprocess
import multiprocessing

def main():
    """Start FastAPI server in production mode."""
    # Get the directory where this script is located
    root_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(root_dir, 'Football-main')
    
    # Check if Football-main directory exists
    if not os.path.exists(api_dir):
        print(f"Error: Football-main directory not found at {api_dir}")
        sys.exit(1)
    
    # Check if production API file exists
    api_file = os.path.join(api_dir, 'fastapi_predictor_production.py')
    if not os.path.exists(api_file):
        print(f"Error: fastapi_predictor_production.py not found at {api_file}")
        sys.exit(1)
    
    # Change to Football-main directory
    os.chdir(api_dir)
    
    # Get configuration from environment
    host = os.getenv('FASTAPI_HOST', '0.0.0.0')
    port = int(os.getenv('FASTAPI_PORT', 8001))
    
    # Calculate optimal worker count
    # Formula: (2 * CPU cores) + 1 for I/O-bound applications
    cpu_count = multiprocessing.cpu_count()
    workers = int(os.getenv('FASTAPI_WORKERS', cpu_count * 2 + 1))
    
    # Limit workers to reasonable maximum
    max_workers = int(os.getenv('FASTAPI_MAX_WORKERS', 16))
    workers = min(workers, max_workers)
    
    print("=" * 70)
    print("Football Predictor API - Production Mode")
    print("=" * 70)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers} (CPU cores: {cpu_count})")
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    print(f"Health: http://{host}:{port}/health")
    print(f"Metrics: http://{host}:{port}/metrics")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        # Run uvicorn with production settings
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'fastapi_predictor_production:app',
            '--host', host,
            '--port', str(port),
            '--workers', str(workers),
            '--log-level', 'info',
            '--access-log',
            '--timeout-keep-alive', '5',
            '--limit-concurrency', '1000',
            '--limit-max-requests', '10000',
            '--no-reload'  # Never reload in production
        ], check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

