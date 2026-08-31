import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import sys

if __name__ == "__main__":
    args = [
        "-v",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ]
    sys.exit(pytest.main(args))
