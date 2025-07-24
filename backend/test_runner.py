#!/usr/bin/env python3
"""
Test runner script for backend tests
"""
import sys
import subprocess
import os


def run_tests():
    """Run backend tests with various options"""
    
    # Ensure we're in the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Default pytest command
    cmd = ["pytest"]
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "coverage":
            # Run with coverage
            cmd = ["pytest", "--cov=app", "--cov-report=html", "--cov-report=term"]
        elif sys.argv[1] == "verbose":
            # Run with verbose output
            cmd.append("-vv")
        elif sys.argv[1] == "quick":
            # Run only quick tests (exclude slow/integration)
            cmd.extend(["-m", "not slow and not integration"])
        elif sys.argv[1] == "integration":
            # Run only integration tests
            cmd.extend(["-m", "integration"])
        else:
            # Pass through any other arguments
            cmd.extend(sys.argv[1:])
    
    # Run the tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())