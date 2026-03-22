import argparse
from importlib.metadata import PackageNotFoundError, version
from redis_server.main3 import main3

DIST_NAME = "my-redis-server"

def get_version():
    try:
        return version(DIST_NAME)
    except PackageNotFoundError:
        return "0.0.0"  # fallback for non-installed source-tree run

def main():
    parser = argparse.ArgumentParser(prog="redis-server")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    args = parser.parse_args()

    if args.version:
        print(get_version())
        return

    main3()

if __name__ == "__main__":
    main()