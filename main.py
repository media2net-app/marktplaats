#!/usr/bin/env python3
"""
Main entry point for Railway deployment
Railway automatically looks for main.py or app.py in the root
"""
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Import and run the worker
from railway_worker import main

if __name__ == '__main__':
    main()

