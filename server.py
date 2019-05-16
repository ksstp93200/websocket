from websocket_server import WebsocketServer
import json
import os

port = int(os.environ.get('PORT', 5000))

music_queue = list()

def new_client(client, server):
    print("Client has joined.")
    send_msg = dict()
    send_msg['type'] = "playlist"
    send_msg['data'] = music_queue
    server.send_message(client, json.dumps(send_msg))

def client_left(client, server):
    print("Client disconnected")


def message_back(client, server, message):
    send_msg = dict()
    rcv = json.loads(message)
    if(rcv["type"] == "stop"):
        send_msg['type'] = "stop"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == "play"):
        send_msg['type'] = "play"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == 'url'):
        music_queue.append(message)
        send_msg['type'] = "add"
        send_msg['data'] = rcv["data"]
        server.send_message_to_all(json.dumps(send_msg))


server = WebsocketServer(port, host='')

server.set_fn_new_client(new_client)

server.set_fn_client_left(client_left)

server.set_fn_message_received(message_back)

server.run_forever()
