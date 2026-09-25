"""
Quick Diagnostic Tool for LM Studio / Bionic Connection.

Run this script to verify that your local LM Studio server is running and accessible:
    python test_connection.py
"""

import sys
from config import load_config
from llm_client import create_llm_client, test_connection

# Ensure standard UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    print("=" * 60)
    print(" [*] LM Studio / Bionic Connection Diagnostic Tool")
    print("=" * 60)

    config = load_config()
    print(f" -> Target Endpoint: {config.base_url}")
    print(f" -> API Key:         {'*' * (len(config.api_key) - 2) + config.api_key[-2:] if len(config.api_key) > 2 else '***'}")
    print(" ... Testing connection (timeout 5s)...")

    # Short timeout for connection test
    client = create_llm_client(base_url=config.base_url, api_key=config.api_key, timeout=5.0)
    success, message, models = test_connection(client)

    if success:
        print("\n [✓] CONNECTION SUCCESSFUL!")
        print(f" Message: {message}")
        if models:
            print(f"\n Available / Loaded Models ({len(models)}):")
            for m in models:
                print(f"   - {m}")
        else:
            print("\n [i] No specific models returned. LM Studio will serve the currently loaded model.")
    else:
        print("\n [X] CONNECTION FAILED!")
        print(f" Reason: {message}")
        print("\n Troubleshooting Tips:")
        print(" 1. Open LM Studio on your machine or 'bionic'.")
        print(" 2. Navigate to the 'Local Server' tab (icon `<->` on the left sidebar).")
        print(" 3. Ensure a model is loaded in the top dropdown.")
        print(" 4. Click 'Start Server' and verify the port (default: 1234).")
        print(" 5. Check that your .env file has the matching URL: LM_STUDIO_BASE_URL=...")
        sys.exit(1)


if __name__ == "__main__":
    main()
