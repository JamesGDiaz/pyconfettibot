# this will route the flow of the program to the different modules, manage outputs and so on
import time
from ocr import ocr
from networking import server
from question import Question
from os import listdir
from os.path import isfile, join
from solvers import handler
from colorama import Fore, Back, Style


def singleFile(filename):
    print(f"Analizando imagen {filename}")
    millisstart = int(round(time.time() * 1000))
    myquestion = ocr.getQuestionfromFilename(filename)
    millisend = int(round(time.time() * 1000))
    if myquestion.exito:
        myquestion.posible_respuesta = handler.answer_question(
            myquestion.pregunta, myquestion.respuestas)
        print(Fore.BLUE + f"OCR took {millisend-millisstart}ms\n")
    else:
        print("ERROR")


def allInFolder(path):
    print(f"Analizando todas las imagenes en {path}...")
    imagelist = [image for image in listdir(path)
                 if isfile(join(path, image))]
    for image in imagelist:
        singleFile(join(path, image))


def autonomousMode():
    print("\nconfettibot: modo autonomo\n")
    server.startserver()


def searchForAnswers(question, answers):
    handler.answer_question(question, answers)
