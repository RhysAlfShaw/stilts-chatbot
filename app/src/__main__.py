import argparse
import uvicorn


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Host IP address", type=str, default="0.0.0.0")
    parser.add_argument("--port", "-p", help="Port number", type=int, default=1007)
    parser.add_argument(
        "--reload", "-r", help="Reload on code changes", action="store_true"
    )
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_args()
    uvicorn.run("src.main:app", host=args.host, port=args.port, reload=args.reload)