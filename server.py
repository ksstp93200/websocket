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
time_queue = list()

def updatequeue(ptime, ctime):
    pastsec = int(ctime - ptime)
    if pastsec >= remaintime:
        pastsec -= remaintime
        try:
            music_queue.pop(0)
            time_queue.pop(0)
        except:
            return -1
        for i in range(len(music_queue)):
            if pastsec >= time_queue[0]:
                pastsec -= time_queue[0]
                try:
                    music_queue.pop(0)
                    time_queue.pop(0)
                except:
                    return -1
            else:
                return time_queue[0] - pastsec
        return -1
    else:
        return remaintime - pastsec

def new_client(client, server):
    print("Client has joined.")
    send_msg = dict()
    mutex.acquire()
    if(status):
        currenttime = time.time()
        remaintime = updatequeue(playtime, currenttime)
        if remaintime == -1:
            send_msg['data'] = []
            send_msg['status'] = False
            status = False
        else:
            playtime = currenttime
            send_msg['data'] = copy.copy(music_queue)
            send_msg['time'] = copy.copy(time_queue[0] - remaintime)
            send_msg['status'] = True
    else:
        send_msg['data'] = copy.copy(music_queue)
        send_msg['time'] = copy.copy(time_queue[0] - remaintime)
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
        currenttime = time.time()
        remaintime = updatequeue(playtime, currenttime)
        mutex.release()
        send_msg['type'] = "stop"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == "play" and not status and len(music_queue) > 0):
        status = True
        mutex.acquire()
        playtime = time.time()
        mutex.release()
        send_msg['type'] = "play"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == 'url'):
        mutex.acquire()
        music_queue.append(rcv["data"])
        mutex.release()
        time_queue.append(rcv["time"])
        send_msg['type'] = "add"
        send_msg['data'] = rcv["data"]
        server.send_message_to_all(json.dumps(send_msg))


server = WebsocketServer(port, host='')

server.set_fn_new_client(new_client)

server.set_fn_client_left(client_left)

server.set_fn_message_received(message_back)

server.run_forever()
