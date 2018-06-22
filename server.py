import asyncio
import websockets
import json
import sys
import aiohttp
from websocket import create_connection
import re
import functools

active_client_connections = {}
active_server_connections = {}
# TODO: move server locations to config or serve through discovery service
server_locations = {
    'server1': 'ws://localhost:8765',
    'server2': 'ws://localhost:8766'
}
peer_server_id = ''
peer_server_connection = [None]
peer_server_connection_url = None
persistence_service_url = 'http://localhost:8080/messages'


# connection path formats:
#   /server/<serverid>
#   /client/<username>
connection_path = re.compile("^\/(?P<type>[^\/]+)\/(?P<id>[^\/]+)$")


async def persist_msg(json_msg):
    async with aiohttp.ClientSession() as session:
        await session.post(persistence_service_url, json=json_msg)


async def handle_client_messages(ws, username, peer_server):
    while True:
        try:
            msg = json.loads(await ws.recv())
        except websockets.exceptions.ConnectionClosed:
            print(f'Connection closed for {username}')
            del active_client_connections[username]
            break
        else:
            print(f'processing client msg: {msg}')
            to_user_id = msg['to_user_id']
            if to_user_id in active_client_connections:
                user_msg = f"from_user: {username}, message: {msg['message']}"
                await active_client_connections[to_user_id].send(user_msg)
                await ws.send(f"Message delivered to {to_user_id}!")
                await persist_msg({'from': username, 'to': to_user_id, 'content': msg['message']})
            elif peer_server:
                msg['type'] = 'FORWARD_TO_CLIENT'
                msg['from_user_id'] = username
                peer_server.send(json.dumps(msg))
            else:
                await ws.send(f"Message delivery failed. {to_user_id} is offline.")


async def handle_server_messages(ws, serverid, peer_server):
    while True:
        try:
            msg = json.loads(await ws.recv())
            print(f'processing server msg: {msg}')
        except websockets.exceptions.ConnectionClosed:
            print(f'Connection closed for {serverid}')
            del active_server_connections[serverid]
            break
        else:
            if msg['type'] == 'FORWARD_TO_CLIENT':
                if msg['to_user_id'] in active_client_connections:
                    user_msg = f"from_user: {msg['from_user_id']}, message: {msg['message']}"
                    await active_client_connections[msg['to_user_id']].send(user_msg)
                    await persist_msg({'from': msg['from_user_id'],
                                       'to': msg['to_user_id'],
                                       'content': msg['message']})
                    # send originating server success report
                    s_msg = {'type': 'DELIVERY_REPORT',
                             'to_user_id': msg['from_user_id'],
                             'message': f"Message delivered to {msg['to_user_id']}."}
                    peer_server.send(json.dumps(s_msg))
                else:
                    # send originating server failure report
                    e_msg = {'type': 'DELIVERY_REPORT',
                             'to_user_id': msg['from_user_id'],
                             'message': f"Message delivery failed. {msg['to_user_id']} is offline."}
                    peer_server.send(json.dumps(e_msg))
            else: # DELIVERY_REPORT
                if msg['to_user_id'] in active_client_connections:
                    await active_client_connections[msg['to_user_id']].send(msg['message'])


async def handle_connections(ws, path, peer_server_connection, peer_server_connection_url):
    m = connection_path.match(path)
    if not m:
        print('Invalid connection path')
        return

    ## hack (figure out better way to lazy load peer_server_connection ##
    if peer_server_connection[0] == None:
        peer_server_connection[0] = create_connection(peer_server_connection_url)
    ####

    type = m[1]
    id   = m[2]
    print(f'type: {type}, id: {id}')
    if type == 'server':
        active_server_connections[id] = ws
        await handle_server_messages(ws, id, peer_server_connection[0])
    elif type == 'client':
        active_client_connections[id] = ws
        await handle_client_messages(ws, id, peer_server_connection[0])
    else:
        print('ERROR: invalid connection type')
        return


def run_server(srv_id, port_num, peer_server_id):
    peer_server_connection_url = f'{server_locations[peer_server_id]}/server/{srv_id}'
    start_server = websockets.serve(functools.partial(handle_connections,
                                                      peer_server_connection=peer_server_connection,
                                                      peer_server_connection_url=peer_server_connection_url),
                                    'localhost', port_num)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    if peer_server_connection[0]:
        peer_server_connection[0].close()


if len(sys.argv) != 4:
    print("Correct usage: server.py <id> <port_number> <peer_server_id>")
    exit(1)


run_server(sys.argv[1], int(sys.argv[2]), sys.argv[3])
