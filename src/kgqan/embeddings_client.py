import socket
import selectors
import traceback
import libclient as libclient
import time
import os


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


def drop_common_word(wlist1, wlist2):
    output1 = []
    output2 = []
    for word in wlist1:
        if word not in wlist2:
            output1.append(word)

    for word in wlist2:
        if word not in wlist1:
            output2.append(word)

    if len(output1) == 0:
        output1 = wlist1

    if len(output2) == 0:
        output2 = wlist2

    return output1, output2


def n_similarity(mwe1, mwe2):
    # mwe1 = [w for w in mwe1 if w not in ['of', 'into', 'be']]
    # mwe2 = [w for w in mwe2 if w not in ['of', 'into', 'be']]
    # case 1: Department Code, Zip Code
    # Case 2: mission, next mission
    # if mwe1 == mwe2:
    #     return 1
    #
    # mwe1, mwe2 = drop_common_word(mwe1, mwe2)
    # print("Lists ", mwe1)
    # print(mwe2)

    mwe1 = ' '.join(mwe1)
    mwe2 = ' '.join(mwe2)

    sel = selectors.DefaultSelector()
    host = os.getenv("WORD_EMBEDDING_HOST", "0.0.0.0")
    port = int(os.getenv("WORD_EMBEDDING_PORT", '9600'))
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
    start_time = time.time()
    for i in range(1000):
        sim = n_similarity(['intel'], ['intel', '80486dx'])
        # sim = n_similarity(['mohamed'], ['ahmed'])
        # print(sim)
    end_time = time.time()
    print(end_time-start_time)
