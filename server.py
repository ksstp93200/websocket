from websocket_server import WebsocketServer
import json
import os
import time
import threading
import copy

mutex = threading.Lock()

status = False

playtime = None

remaintime = None

port = int(os.environ.get('PORT', 5000))

music_queue = list()

def gettime():
    localtime = time.localtime(time.time())
    return localtime

def updatequeue(ptime, ctime):
    

def new_client(client, server):
    print("Client has joined.")
    send_msg = dict()
    mutex.acquire()
    if(status):
        currenttime = gettime()
        remaintime = updatequeue(playtime, currenttime)
        playtime = currenttime
        send_msg['data'] = copy.copy(music_queue)
        send_msg['time'] = copy.copy(remaintime)
        send_msg['status'] = True
    else:
        send_msg['data'] = copy.copy(music_queue)
        send_msg['time'] = copy.copy(remaintime)
        send_msg['status'] = False
    mutex.release()
    send_msg['type'] = "playlist"
    server.send_message(client, json.dumps(send_msg))

def client_left(client, server):
    print("Client disconnected")


def message_back(client, server, message):
    send_msg = dict()
    rcv = json.loads(message)
    if(rcv["type"] == "stop" and status):
        mutex.acquire()
        status = False
        currenttime = gettime()
        remaintime = updatequeue(playtime, currenttime)
        mutex.release()
        send_msg['type'] = "stop"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == "play" and not status):
        status = True
        mutex.acquire()
        playtime = gettime()
        mutex.release()
        send_msg['type'] = "play"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == 'url'):
        music_queue.append(rcv["data"])
        send_msg['type'] = "add"
        send_msg['data'] = rcv["data"]
        server.send_message_to_all(json.dumps(send_msg))


server = WebsocketServer(port, host='')

server.set_fn_new_client(new_client)

server.set_fn_client_left(client_left)

server.set_fn_message_received(message_back)

server.run_forever()
