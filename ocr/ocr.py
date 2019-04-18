# this module will perform OCR in the provided image, attempting to separate the posed question and the three possible answers in a json like object
# works around 98-99% of the time
import pytesseract
import json
import cv2
from PIL import Image
from math import ceil, floor
import time
import numpy
import base64
import colorama
from colorama import Fore, Back, Style

from question import Question


def base64toimage(uri):
    encoded_data = uri.split(',')[1]
    nparr = numpy.fromstring(base64.b64decode(encoded_data), numpy.uint8)
    image = cv2.imdecode(nparr)
    return image


def binarystring2image(data):
    nparr = numpy.frombuffer(data, dtype=numpy.int8)
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return image


def filename2cv2image(filename):
    # load the image
    filename = filename.strip()
    image = cv2.imread(filename)
    return image


def runOcr(image, crop=False):
    tstart = int(round(time.time() * 1000))
    scale = 0.7
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_LINEAR)
    #cv2.imshow('image', image)
    # cv2.waitKey(0)
    # crop the image if it comes fullsize, the question box is around 58% of the height of the screen
    if crop:
        starty = floor(image.shape[0]*0.58)
        image = image[starty: image.shape[0], 0: image.shape[1]]

    # crop the question
    # around 34% of this box is where the division between question and answers is
    y = floor(image.shape[0] * 0.34)
    question_box = image[0:y, 0: image.shape[1]]
    # crop and preprocess the answers
    answers_box = image[y: image.shape[0], 0: image.shape[1]]
    #answers_box = preprocess(answers_box)
    # OCR the cropped image
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
    #cv2.imshow('image', image)
    maxIntensity = 255.0  # depends on dtype of image data

    # Parameters for manipulating image data
    phi = 1
    theta = 1

    # Increase intensity such that
    # dark pixels become much brighter,
    # bright pixels become slightly bright
    contrastedimage = (maxIntensity/phi)*(image/(maxIntensity/theta))**0.8
    contrastedimage = numpy.array(contrastedimage, dtype=numpy.int8)
    #cv2.imshow('image contrasted', contrastedimage)
    # cv2.waitKey(0)
    return contrastedimage
