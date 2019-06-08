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
title_queue = list()

def updatequeue(ptime, ctime):
    global status
    global playtime
    global remaintime
    global music_queue
    global time_queue
    global title_queue
    pastsec = int(ctime - ptime)
    if remaintime == None:
        for i in range(len(music_queue)):
            if pastsec >= time_queue[0]:
                pastsec -= time_queue[0]
                try:
                    music_queue.pop(0)
                    title_queue.pop(0)
                    time_queue.pop(0)
                except:
                    return -1
            else:
                return time_queue[0] - pastsec
        return -1
    elif pastsec >= remaintime:
        pastsec -= remaintime
        try:
            music_queue.pop(0)
            time_queue.pop(0)
            title_queue.pop(0)
        except:
            return -1
        for i in range(len(music_queue)):
            if pastsec >= time_queue[0]:
                pastsec -= time_queue[0]
                try:
                    music_queue.pop(0)
                    title_queue.pop(0)
                    time_queue.pop(0)
                except:
                    return -1
            else:
                return time_queue[0] - pastsec
        return -1
    else:
        return remaintime - pastsec

def new_client(client, server):
    global status
    global playtime
    global remaintime
    print("Client has joined.")
    send_msg = dict()
    mutex.acquire()
    if(status):
        currenttime = time.time()
        remaintime = updatequeue(playtime, currenttime)
        if remaintime == -1:
            remaintime = None
            send_msg['data'] = []
            send_msg['title'] = []
            send_msg['status'] = False
            status = False
        else:
            print("update time")
            playtime = currenttime
            send_msg['data'] = copy.copy(music_queue)
            send_msg['title'] = copy.copy(title_queue)
            send_msg['time'] = copy.copy(time_queue[0] - remaintime)
            send_msg['status'] = True
    elif(len(music_queue) > 0):
        print("ok")
        send_msg['data'] = copy.copy(music_queue)
        send_msg['title'] = copy.copy(title_queue)
        if remaintime != None:
            send_msg['time'] = copy.copy(time_queue[0] - remaintime)
        send_msg['status'] = False
    else:
        send_msg['data'] = []
        send_msg['title'] = []
        send_msg['status'] = False
    mutex.release()
    send_msg['type'] = "playlist"
    server.send_message(client, json.dumps(send_msg))

def client_left(client, server):
    print("Client disconnected")


def message_back(client, server, message):
    global status
    global playtime
    global remaintime
    send_msg = dict()
    try:
        rcv = json.loads(message)
    except:
        return
    if(rcv["type"] == "stop" and status):
        mutex.acquire()
        status = False
        currenttime = time.time()
        remaintime = updatequeue(playtime, currenttime)
        if remaintime == -1:
            remaintime = None
        mutex.release()
        send_msg['type'] = "stop"
        server.send_message_to_all(json.dumps(send_msg))
    if(rcv["type"] == "skip" and len(music_queue) > 0):
        mutex.acquire()
        playtime = time.time()
        remaintime = None
        music_queue.pop(0)
        title_queue.pop(0)
        time_queue.pop(0)
        if len(music_queue) <= 0:
            status = False
        mutex.release()
        send_msg['type'] = "skip"
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
        if(status):
            currenttime = time.time()
            remaintime = updatequeue(playtime, currenttime)
            if remaintime == -1:
                remaintime = None
            else:
                print("update time")
                playtime = currenttime
        music_queue.append(rcv["data"])
        title_queue.append(rcv["title"])
        print(rcv["title"])
        mutex.release()
        time_queue.append(int(rcv["time"]))
        send_msg['type'] = "add"
        send_msg['data'] = rcv["data"]
        send_msg['title'] = rcv["title"]
        server.send_message_to_all(json.dumps(send_msg))


server = WebsocketServer(port, host='')

server.set_fn_new_client(new_client)

server.set_fn_client_left(client_left)

server.set_fn_message_received(message_back)

server.run_forever()
