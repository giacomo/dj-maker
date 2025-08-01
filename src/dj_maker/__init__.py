import sys
from dj_maker.main import app

def main() -> None:
    args = sys.argv[1:]
    if not args:
        app(["--help"])
    else:
        app(args)