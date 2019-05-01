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
import ssl
import pathlib
import time
from question import Question
from solvers import handler
from ocr import ocr

myquestion = Question(exito=False)
logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


async def sendtowebapp(message):
    webapp_url = "ws://shrouded-beyond-11417.herokuapp.com/api/admin/relay"
    test_url = "ws://localhost:19011/api/admin/relay"
    url = webapp_url
    try:
        async with websockets.connect(url) as ws_node:
            await ws_node.send(message)
    except Exception:
        logger.error(f"Error al enviar al servidor en {url}")


class wsMessage:
    class Type:
        INFO = "INFO"
        QUESTION = "QUESTION"
        ANSWER = "ANSWER"
        ERROR = "ERROR"

    def getJson(self):
        return json.dumps({"type": self.type, "message": self.message})

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
    Tstart = int(round(time.time() * 1000))
    logger.info("Datos recibidos!")
    info = f"Procesando datos ({len(data)} bytes)..."
    logger.info(info)
    try:
        image = ocr.binarystring2image(data)
        myquestion = ocr.runOcr(image)
        pregunta = wsMessage(type=wsMessage.Type.QUESTION,
                             message=myquestion.pregunta).getJson()
        await websocket.send(pregunta)
        myquestion.posible_respuesta = await handler.answer_question(myquestion.pregunta, myquestion.respuestas)
        myanswer = wsMessage(type=wsMessage.Type.ANSWER,
                             message=myquestion.getAnswer()).getJson()
        await websocket.send(myanswer)
        Tend = int(round(time.time() * 1000))
        await websocket.send(wsMessage(type=wsMessage.Type.INFO, message=f"Esta búsqueda tardó {(Tend-Tstart)/1000} segundos").getJson())
    except:
        e = sys.exc_info()
        logger.error(e)


async def consumer_handler(websocket, path):
    logger.info("Conexion realizada. Esperando datos")
    async for data in websocket:
        await consumer(websocket, data)


def startserver():
    localip = "localhost"  # getLocalIp()
    port = 19010
    logger.info(f"Esperando conexion en 'ws://{localip}:{port}'...")
    coro = websockets.serve(
        consumer_handler, localip, port, max_size=524288)
    asyncio.get_event_loop().run_until_complete(
        coro)
    asyncio.get_event_loop().run_forever()
