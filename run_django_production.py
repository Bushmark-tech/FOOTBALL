"""
Production startup script for Django server.
Uses Gunicorn with proper worker configuration for scalability.
"""
import os
import sys
import subprocess
import multiprocessing

def main():
    """Start Django server in production mode using Gunicorn."""
    # Get the directory where this script is located
    root_dir = os.path.dirname(os.path.abspath(__file__))
    django_dir = root_dir  # Script is already in the project root
    
    # Check if manage.py exists
    manage_py = os.path.join(django_dir, 'manage.py')
    if not os.path.exists(manage_py):
        print(f"Error: manage.py not found at {manage_py}")
        sys.exit(1)
    
    # Check if gunicorn_config.py exists
    gunicorn_config = os.path.join(django_dir, 'gunicorn_config.py')
    if not os.path.exists(gunicorn_config):
        print(f"Warning: gunicorn_config.py not found. Using default settings.")
        gunicorn_config = None
    
    # Change to Football-main directory
    os.chdir(django_dir)
    
    # Set production settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings_production')
    
    # Get configuration
    bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
    cpu_count = multiprocessing.cpu_count()
    workers = int(os.getenv('GUNICORN_WORKERS', cpu_count * 2 + 1))
    
    print("=" * 70)
    print("LEON GAMES PRO Django - Production Mode")
    print("=" * 70)
    print(f"Bind: {bind}")
    print(f"Workers: {workers} (CPU cores: {cpu_count})")
    print(f"Settings: football_predictor.settings_production")
    print(f"Server: http://{bind.split(':')[0]}:{bind.split(':')[1]}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    try:
        if os.name == 'nt':
            print("(!) Windows detected: Using 'manage.py runserver' for compatibility (Gunicorn is Unix-only).")
            print("(!) Note: This is for local testing only. Do not use for real production.")
            
            # Use 'python manage.py runserver' on Windows
            cmd = [
                sys.executable, 'manage.py', 'runserver', 
                bind if ':' in bind else f"0.0.0.0:{bind}",
                '--settings=football_predictor.settings_production'
            ]
        else:
            # Build gunicorn command for Unix/Linux
            cmd = [
                sys.executable, '-m', 'gunicorn',
                'football_predictor.wsgi:application',
                '--bind', bind,
                '--workers', str(workers),
                '--worker-class', 'sync',
                '--timeout', '30',
                '--keepalive', '5',
                '--max-requests', '1000',
                '--max-requests-jitter', '50',
                '--preload',
                '--access-logfile', '-',
                '--error-logfile', '-',
                '--log-level', 'info'
            ]
        
        if gunicorn_config and os.name != 'nt':
            cmd.extend(['--config', 'gunicorn_config.py'])
        
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running Django server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

