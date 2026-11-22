"""Avvio dello strumento web per le immagini di mappe ed eventi."""
import argparse
import socket
import threading
import webbrowser

import uvicorn

from tools.image_tool.app import create_app
from tools.image_tool.conversion import ImageToolError

DEFAULT_PORT = 8765


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Strumento locale per importare immagini di mappe ed eventi"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"porta locale (default {DEFAULT_PORT})",
    )
    parser.add_argument("--no-browser", action="store_true", help="non aprire il browser")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("La porta deve essere tra 1 e 65535")
    if not port_is_free(args.port):
        parser.error(f"La porta {args.port} è occupata: usa --port con un'altra porta")
    try:
        app = create_app()
    except (ImageToolError, OSError) as exc:
        parser.error(str(exc))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Strumento immagini pronto su {url} - Ctrl+C per fermare", flush=True)
    if not args.no_browser:
        timer = threading.Timer(1.0, webbrowser.open, args=[url])
        timer.daemon = True
        timer.start()
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
