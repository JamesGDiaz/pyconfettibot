# this module will wait for an image to be sent by the client (iOS, Android, or the test web client) and analyze it accordingly
import sys
import json
import websockets
import asyncio
import logging
import cv2
import numpy as np
import socket
import enum
import time
from question import Question
from solvers import handler
from ocr import ocr

myquestion = Question(exito=False)
CLIENTS = list()


async def sendtowebapp(message):
    try:
        async with websockets.connect("wss://shrouded-beyond-11417.herokuapp.com/broadcast") as ws_node:
            await ws_node.send(message)
    except Exception:
        print("Error al enviar al servidor node")


class wsMessage:
    class Type:
        INFO = "INFO"
        QUESTION = "QUESTION"
        ANSWER = "ANSWER"
        ERROR = "ERROR"

    def getJson(self):
        return json.dumps({'type': self.type, 'message': self.message})

    def __init__(self, type='null', message='null'):
        super()
        self.type = type
        self.message = message


def getLocalIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


async def consumer(websocket, data):
    millisstart = int(round(time.time() * 1000))
    print("Datos recibidos!")
    info = f"Procesando datos ({len(data)} bytes)..."
    await websocket.send(wsMessage(type=wsMessage.Type.INFO, message=info).getJson())
    print(info)
    try:
        image = ocr.binarystring2image(data)
        myquestion = ocr.runOcr(image)
        pregunta = wsMessage(type=wsMessage.Type.QUESTION,
                             message=myquestion.pregunta).getJson()
        await sendtowebapp(pregunta)
        await asyncio.wait([client.send(pregunta) for client in CLIENTS])
        myquestion.posible_respuesta = await handler.answer_question(myquestion.pregunta, myquestion.respuestas)
        mymessage = wsMessage(type=wsMessage.Type.ANSWER,
                              message=myquestion.getAnswer()).getJson()
        await asyncio.wait([client.send(mymessage) for client in CLIENTS])
        await sendtowebapp(mymessage)
    except:
        e = sys.exc_info()
        print(e)
        await websocket.send(wsMessage(type=wsMessage.Type.ERROR, message="Hubo un error al procesar los datos recibidos :(").getJson())
    millisend = int(round(time.time() * 1000))
    print(f"WebSocket took {millisend-millisstart}ms")


async def consumer_handler(websocket, path):
    CLIENTS.append(websocket)
    await websocket.send(wsMessage(type=wsMessage.Type.INFO, message="Conexion realizada. Esperando datos...").getJson())
    print("Conexion realizada. Esperando datos")
    try:
        async for data in websocket:
            await consumer(websocket, data)
    finally:
        CLIENTS.remove(websocket)


def startserver():
    localip = getLocalIp()
    port = 19010
    print(f"Esperando conexion en 'ws://{localip}:{port}'...")
    coro = websockets.serve(
        consumer_handler, localip, port, max_size=5242880)
    asyncio.get_event_loop().run_until_complete(
        coro)
    asyncio.get_event_loop().run_forever()


logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
