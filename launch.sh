#!/bin/bash
# Unified Launcher Wrapper for Linux/Mac
# This script finds Python and executes the unified launcher

# Find Python
for cmd in python3 python; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" -c "import sys; print(str(sys.version_info.major) + '.' + str(sys.version_info.minor))" 2>/dev/null)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        # Check for Python 3.11+
        if [[ "$major" -gt 3 ]] || [[ "$major" -eq 3 && "$minor" -ge 11 ]]; then
            echo "Found Python: $cmd"
            "$cmd" unified_launcher.py "$@"
            exit $?
        fi
    fi
done

# Python not found
echo ""
echo "ERROR: Python 3.11+ not found!"
echo ""
echo "Please install Python 3.11+ and try again."
echo "Download from: https://www.python.org/downloads/"
echo ""
exit 1

