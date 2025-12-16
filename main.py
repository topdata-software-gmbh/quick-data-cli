#!/usr/bin/env python3
"""Entry point for Quick Data CLI."""

import sys
import os

# Add src to Python path so we can import the CLI package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from quick_data_cli.cli import main


if __name__ == "__main__":
    main()
