#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Add the parent directory to the Python path to allow for absolute imports.
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(APP_ROOT, ".."))

# Import provider and tool modules to allow them to be discovered.
import minimal_provider # Adjusted import path
import minimal_tool       # Adjusted import path

# For Dify plugins, the main.py should not run Flask directly
# The Dify plugin daemon handles the communication
# This file serves as the entry point for module discovery

if __name__ == "__main__":
    # The plugin should be managed by the Dify daemon
    # No Flask app should be started here
    print("Plugin modules loaded successfully")
    
    # Keep the process alive for the daemon to communicate
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass 