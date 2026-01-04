#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Load .env file for local development/testing
    try:
        from pathlib import Path
        env_path = Path(__file__).resolve().parent / '.env'
        if env_path.exists():
            print(f"[*] Loading environment from {env_path}")
            with open(env_path, encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            # Remove surrounding quotes
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            os.environ[key] = value
                            # print(f"  - Set {key}") # Debug
                        except ValueError:
                            pass
        else:
            print(f"[!] No .env file found at {env_path}")
    except Exception as e:
        print(f"[!] Error loading .env: {e}")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'football_predictor.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 