"""Allow `python -m pixa` alongside the `pixa` console script."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
