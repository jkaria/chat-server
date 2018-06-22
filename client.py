import websocket
import _thread as thread
import sys
import re
import json


def on_message(ws, message):
    print(f"received > {message}")

def on_error(ws, error):
    print(f"error > {error}")

def on_close(ws):
    print("Server connection closed")

def on_open(ws):
    def run(*args):
        msg_format = re.compile("(.+):\s(.+)")
        while True:
            msg = input("<Enter message in format 'to_user_id: msg' (enter 'quit' to exit)>:\n")
            if msg == 'quit':
                break
            m = msg_format.match(msg)
            if not m:
                print("invalid message format")
                continue
            ws.send(json.dumps({'to_user_id': m[1], 'message': m[2]}))
            print(f"< sending: {m[2]}...")

        ws.close()
        print("Closed connection. Thread terminating...")

    #TODO: look into async input to get read of this thread
    thread.start_new_thread(run, ())


def connect_to_server(srv_port, username):
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"ws://localhost:{srv_port}/client/{username}",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

if len(sys.argv) != 3:
    print("Correct usage: server.py <server_port_number> <username>")
    exit(1)

connect_to_server(int(sys.argv[1]), str(sys.argv[2]))
