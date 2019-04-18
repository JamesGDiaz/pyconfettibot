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


async def sendtowebapp(message):
    webapp_url = "ws://shrouded-beyond-11417.herokuapp.com/api/admin/relay"
    test_url = "ws://localhost:19011/api/admin/relay"
    url = webapp_url
    try:
        async with websockets.connect(url) as ws_node:
            await ws_node.send(message)
    except Exception:
        print(f"Error al enviar al servidor en {url}")


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
    runocr = True

    millisstart = int(round(time.time() * 1000))
    print("Datos recibidos!")
    if runocr:
        info = f"Procesando datos ({len(data)} bytes)..."
        await websocket.send(wsMessage(type=wsMessage.Type.INFO, message=info).getJson())
        print(info)
        try:
            image = ocr.binarystring2image(data)
            myquestion = ocr.runOcr(image)
            pregunta = wsMessage(type=wsMessage.Type.QUESTION,
                                 message=myquestion.pregunta).getJson()
            await sendtowebapp(pregunta)
            myquestion.posible_respuesta = await handler.answer_question(myquestion.pregunta, myquestion.respuestas)
            mymessage = wsMessage(type=wsMessage.Type.ANSWER,
                                  message=myquestion.getAnswer()).getJson()
            await sendtowebapp(mymessage)
        except:
            e = sys.exc_info()
            print(e)
            await sendtowebapp(wsMessage(type=wsMessage.Type.INFO, message="Hubo un error al procesar la pregunta :(").getJson())
    else:
        jsondata = json.loads(data)
        myquestion = Question(
            jsondata['exito'], jsondata['pregunta'], jsondata['respuesta1'], jsondata['respuesta2'], jsondata['respuesta3'])
        print(myquestion.getPretty())
        pregunta = wsMessage(type=wsMessage.Type.QUESTION,
                             message=myquestion.pregunta).getJson()
        await sendtowebapp(pregunta)
        myquestion.posible_respuesta = await handler.answer_question(myquestion.pregunta, myquestion.respuestas)
        respuesta = wsMessage(type=wsMessage.Type.ANSWER,
                              message=myquestion.getAnswer()).getJson()
        await sendtowebapp(respuesta)

    millisend = int(round(time.time() * 1000))
    await sendtowebapp(wsMessage(type=wsMessage.Type.INFO,
                                 message=f"Esta búsqueda tardó {(millisend-millisstart)/1000} segundos").getJson())
    print(f"WebSocket took {millisend-millisstart}ms")


async def consumer_handler(websocket, path):
    print("Conexion realizada. Esperando datos")
    async for data in websocket:
        await consumer(websocket, data)


def startserver():
    localip = getLocalIp()
    port = 19010
    print(f"Esperando conexion en 'ws://{localip}:{port}'...")
    coro = websockets.serve(
        consumer_handler, localip, port, max_size=524288)
    asyncio.get_event_loop().run_until_complete(
        coro)
    asyncio.get_event_loop().run_forever()


logger = logging.getLogger('websockets')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
