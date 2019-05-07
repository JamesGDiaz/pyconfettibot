# this will route the flow of the program to the different modules, manage outputs and so on
import time
import asyncio
import socket
import daemon
import random
import json

from ocr import ocr
from networking import server
from question import Question
from os import listdir
from os.path import isfile, join
from solvers import handler
from colorama import Fore, Back, Style
import result_analysis


def singleFile(filename):
    print(f"Analizando imagen {filename}")
    tstart = int(round(time.time() * 1000))
    myquestion = ocr.getQuestionfromFilename(filename)

    coro = handler.answer_question(
        myquestion.pregunta, myquestion.respuestas)
    try:
        myquestion.respuestaPropuesta = asyncio.get_event_loop().run_until_complete(
            coro)
    except Exception as e:
        print(e)
    tend = int(round(time.time() * 1000))
    myquestion.searchTime = tend-tstart
    return myquestion


def allInFolder(path):
    print(f"Analizando todas las imagenes en {path}...")
    imagelist = [image for image in listdir(path)
                 if isfile(join(path, image))]
    for image in imagelist:
        singleFile(join(path, image))


def autonomousMode():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    IP = ""
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()

    print("\nconfettibot: modo autonomo\n")
    print("Iniciando daemon...")
    server.startserver(IP)


def daemonMode():
    print("\nconfettibot: modo autonomo\n")
    print("Iniciando daemon...")
    fstdout = open("pyconfettibot-out.log", "w")
    fstderr = open("pyconfettibot-error.log", "w")
    with daemon.DaemonContext(stdout=fstdout, stderr=fstderr):
        server.startserver('127.0.0.1')


def writeToFile(path):
    print("\nconfettibot: modo estadistico\n")
    print(f"Analizando todas las imagenes en {path}...")
    result_analysis.writeJSONFile(path)


def analyzeJSONFile(path):
    print("\nconfettibot: modo estadistico\n")
    print(f"Analizando datos en {path}...")
    result_analysis.analyzeJSONFile(path)
