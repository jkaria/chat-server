# chat-server
Python chat server using websockets


    Environment requirements:
        - Python version >= 3.6
        - Additional modules captured in requirements.txt


    Components:

        1. app.py:
            - Flask based app server. Supports message persistance and retrival.

        2. client.py:
            - Websocket based client

        3. server.py:
            - Websocket based server
            - Supports client and peer server connections
            - On receiving a client message forwards the message if destination client is connected to same server otherwise forwards it to the peer server.
            - On receiving a server message forwards the message to destination client and sends back success delivery message back to the originating server to be delivered to originating client. A failure delivery message is sent back if destination client is not connected.
            - Messages are persisted via app server api after successful delivery to destination client


Sample interaction between user1 & user2:

![Alt text](demo/ChatServerDemo.png?raw=true "Sample interaction between user1 and user2")

Fetch all messages for a user:

![Alt text](demo/FetchAllMessages.png?raw=true "Fetch all messages for a user")
