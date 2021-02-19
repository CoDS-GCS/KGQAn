import sys
import socket
import selectors
import traceback
from . import libclient




def create_request(word1, word2):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(word1=word1, word2=word2),
    )


def start_connection(host, port, sel, request):
    addr = (host, port)
    # print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, request)
    sel.register(sock, events, data=message)


def n_similarity(mwe1, mwe2):
    mwe1 = ' '.join(mwe1)
    mwe2 = ' '.join(mwe2)

    sel = selectors.DefaultSelector()
    host, port = '127.0.0.1', 9600
    request = create_request(mwe1, mwe2)

    start_connection(host, port, sel, request)

    result = 0.0
    try:
        while True:
            events = sel.select(timeout=1)
            for key, mask in events:
                message = key.data
                try:
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
            # Check for a socket being monitored to continue.
            if not sel.get_map():
                break
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
    return message.response['result']


if __name__ == '__main__':
    sim = n_similarity(['satellites'], ['moon'])
    # sim = n_similarity(['mohamed'], ['ahmed'])
    print(sim)
