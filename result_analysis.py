import json
from os import listdir
from os.path import isfile, join
import sys
import random
import json
import time
from question import Question
import router
import datetime
import statistics as stats


def writeJSONFile(path):
    tstart = int(round(time.time() * 1000))
    output = "["
    imagelist = [image for image in listdir(path)
                 if isfile(join(path, image))]
    count = 0
    total = len(imagelist)
    everything = list(range(total))
    random.shuffle(everything)
    n = range(total)
    for i in n:
        count += 1
        print(f"\nPregunta {count}/{len(n)}")
        thisquestion = router.singleFile(join(path, imagelist[everything[i]]))
        print(
            f"Cual es la respuesta correcta?\n  1) {thisquestion.getDict()['respuestas'][0]['1']}\n  2) {thisquestion.getDict()['respuestas'][0]['2']}\n  3) {thisquestion.getDict()['respuestas'][0]['3']}")
        #correct_answer_num = input()
        #thisquestion.respuestaCorrecta = thisquestion.getDict()['respuestas'][0][correct_answer_num]
        if i <= max(n)-1:
            output += (thisquestion.getJson() + ",")
        else:
            output += thisquestion.getJson()
    output += "]"
    tend = int(round(time.time() * 1000))
    print(
        f"\nLa busqueda termino en {(tend-tstart)/1000}s, cerrando buffers...")

    filename = "statistics-" + \
        datetime.datetime.now().strftime("YYYY-mm-dd-HH-mm-ss")+".json"
    with open(filename, "w") as f:
        f.write(output)
    f.close()
    analyzeJSONFile(filename)


def analyzeJSONFile(path):
    outputjson = ""
    with open(path, "r") as f:
        outputjson = json.load(f)
    averageSearchTime = 0
    searchTimes = []
    objectCount = len(outputjson)
    succesCount = 0
    correctAnswerCount = 0
    for question in outputjson:
        if question['exito']:
            succesCount += 1
            averageSearchTime += question['searchTime']
            searchTimes.append(question['searchTime'])
            if question['respuestaPropuesta'] == question['respuestaCorrecta']:
                correctAnswerCount += 1
    print(
        "\nResultados\n" +
        "------------------\n" +
        f"Preguntas exitosas: {round(100*succesCount/objectCount,3)}% ({succesCount}/{objectCount})\n" +
        f"Respuestas correctas: {round(100*correctAnswerCount/objectCount,3)}% ({correctAnswerCount}/{objectCount})\n" +
        f"Tiempos de busqueda: \n\tPromedio: {round(stats.mean(searchTimes),2)}ms" +
        f"\n\tMaximo: {max(searchTimes)}ms\n\tMinimo: {min(searchTimes)}ms\n\tMediana: {stats.median(searchTimes)}ms\n\tsigma: {round(stats.pstdev(searchTimes),0)}ms")
