#!/usr/bin/env python3
"""
Quick test script for chatbot
"""

import subprocess
import sys
import time


def test_chatbot():
    """Test chatbot with automated input"""
    print("Testing chatbot...")
    print("=" * 70)

    # Start chatbot process
    process = subprocess.Popen(
        [sys.executable, "chat_interactivo.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # Wait a bit for initialization
    time.sleep(2)

    # Send test messages
    test_messages = ["hola", "quiero cotizar", "salir"]

    output_lines = []
    error_lines = []

    try:
        # Read initial output
        for _ in range(10):
            if process.poll() is not None:
                break
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
            time.sleep(0.1)

        # Send first message
        process.stdin.write("hola\n")
        process.stdin.flush()
        time.sleep(1)

        # Read response
        for _ in range(5):
            if process.poll() is not None:
                break
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
            time.sleep(0.1)

        # Send exit
        process.stdin.write("salir\n")
        process.stdin.flush()
        time.sleep(1)

        # Read remaining output
        stdout, stderr = process.communicate(timeout=2)
        if stdout:
            output_lines.extend(stdout.strip().split("\n"))
        if stderr:
            error_lines.extend(stderr.strip().split("\n"))

    except Exception as e:
        print(f"Error: {e}")
        process.terminate()

    print("\n=== STDOUT ===")
    for line in output_lines:
        if line:
            print(line)

    print("\n=== STDERR ===")
    for line in error_lines:
        if line:
            print(line)

    print("\n=== TEST COMPLETE ===")


if __name__ == "__main__":
    test_chatbot()
