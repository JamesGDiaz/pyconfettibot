# this module will perform OCR in the provided image, attempting to separate the posed question and the three possible answers in a json like object
# works around 98-99% of the time
import pytesseract
import json
import cv2
from PIL import Image
from math import ceil, floor
import time
import numpy as np
import base64
import colorama
from colorama import Fore, Back, Style

from question import Question


def base64toimage(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return image


def binarystring2image(data):
    nparr = np.frombuffer(data, dtype=np.int8)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return image


def filename2cv2image(filename):
    # load the image
    filename = filename.strip()
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    return image


def runOcr(image, crop=False):
    tstart = int(round(time.time() * 1000))

    image = preprocess(image)
    #cv2.imshow('image', image)
    # cv2.waitKey(0)

    # crop the image if it comes fullsize, the question box is around 58% of the height of the screen
    if crop:
        starty = floor(image.shape[0]*0.58)
        image = image[starty: image.shape[0], 0: image.shape[1]]

    # crop the question
    # around 34% of the height of this box is the division between question and answers
    y = floor(image.shape[0] * 0.34)
    question_box = image[0:y, 0: image.shape[1]]
    # crop and preprocess the answers
    answers_box = image[y: image.shape[0], 0: image.shape[1]]
    ocr_pregunta = pytesseract.image_to_string(
        question_box, 'spa', nice=-19)  # spanish
    ocr_respuestas = pytesseract.image_to_string(
        answers_box, 'spa', nice=-19)  # spanish
    try:
        ocr_pregunta = ocr_pregunta.replace('\n', ' ').replace('|', '')

        ocr_respuestas = ocr_respuestas.replace('\n\n', '\n')
        myquestion = Question(True, ocr_pregunta, ocr_respuestas.splitlines()[
            0], ocr_respuestas.splitlines()[1], ocr_respuestas.splitlines()[2])
    except:
        myquestion = Question(exito=False)
    tend = int(round(time.time() * 1000))
    print(Fore.BLUE + f"OCR took {tend-tstart}ms")
    return myquestion


def getQuestionfromFilename(filename):
    image = filename2cv2image(filename)
    myquestion = runOcr(image, crop=True)
    return myquestion


def getQuestionfromBinaryString(data):
    image = filename2cv2image(data)
    myquestion = runOcr(image)
    return myquestion


def getQuestionfromBase64String(uri):
    image = filename2cv2image(uri)
    myquestion = runOcr(image)
    return myquestion


def preprocess(image):
    # crop the image horizontally
    endx = floor(image.shape[1]*0.97)
    image = image[0: image.shape[0], 0: endx]

    scale = 0.8
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    ret, thresh1 = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    preprocessimg = cv2.GaussianBlur(thresh1, (3, 3), 0)
    # cv2.imshow('image', image)
    # cv2.imshow('preproc', preprocessimg)
    # cv2.waitKey(0)
    return preprocessimg
