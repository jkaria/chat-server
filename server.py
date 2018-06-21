import asyncio
import websockets
import json
import sys

active_client_connections = {}

async def handle_connections(ws, path):
    username = path.replace('/', '')
    active_client_connections[username] = ws

    while True:
        try:
            msg = json.loads(await ws.recv())
        except websockets.exceptions.ConnectionClosed:
            print(f'Connection closed for {username}')
            break
        else:
            print(f'processing msg: {msg}')
            to_user_id = msg['to_user_id']
            if to_user_id in active_client_connections:
                await active_client_connections[to_user_id].send(f"from_user_id: {username} | message: {msg['message']}")
                await ws.send(f"Message delivered to {to_user_id}!")
            else:
                await ws.send(f"Message delivery failed. {to_user_id} is offline.")

def run_server(port_num):
    start_server = websockets.serve(handle_connections, 'localhost', port_num)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if len(sys.argv) != 2:
    print("Correct usage: server.py <port_number>")
    exit(1)

run_server(int(sys.argv[1]))
