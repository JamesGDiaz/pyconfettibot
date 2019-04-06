# Here lies a definition of a 'question' class, in order to provide a consistent object that all modules can work with
import json


class Question:
    def __init__(self, exito=False, pregunta='null', respuesta1='null', respuesta2='null', respuesta3='null'):
        super()
        self.exito = exito
        self.pregunta = pregunta
        self.respuestas = [respuesta1, respuesta2, respuesta3]
        self.posible_respuesta = ''

    def getDict(self):
        preguntadict = {
            'exito': self.exito,
            'pregunta': self.pregunta,
            'respuestas':
            [{
                '1': self.respuestas[0],
                '2': self.respuestas[1],
                '3': self.respuestas[2]
            }],
            'posible_respuesta': self.posible_respuesta,
        }
        return preguntadict

    # returns a JSON formatted version of the question data
    def getJson(self):
        return json.dumps(self.getDict(), indent=4)

    # returns a human readable version of the question data
    def getPretty(self):
        if (self.exito):
            prettystr = self.pregunta + '\n· ' + \
                self.respuestas[0] + '\n· ' + \
                self.respuestas[1] + '\n· ' + self.respuestas[2]
        else:
            prettystr = "Hubo un error al reconocer las preguntas y respuestas :("
        return prettystr

    def getAnswer(self):
        if self.exito:
            return self.posible_respuesta
        else:
            return "Sin respuesta :("
