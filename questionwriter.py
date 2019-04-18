import json


class Question:
    def __init__(self, exito=False, pregunta='null', respuesta1='null', respuesta2='null', respuesta3='null'):
        super()
        self.exito = exito
        self.pregunta = pregunta
        self.respuestas = [respuesta1, respuesta2, respuesta3]

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
            'posible_respuesta': 'n',
            'confianza': 'xx%'
        }
        return preguntadict

    # returns a JSON formatted version of the question data
    def getJson(self):
        return json.dumps(self.getDict(), indent=4)

    # returns a human readable version of the question data
    def getPretty(self):
        if (self.exito):
            prettystr = self.pregunta + '\n* ' + \
                self.respuestas[0] + '\n* ' + \
                self.respuestas[1] + '\n* ' + self.respuestas[2]
        else:
            prettystr = "Hubo un error al reconocer las preguntas y respuestas :("
        return prettystr


programacompleto = []
f = open("programacompleto.json", "a")
for i in range(10):
    q = input(f"Pregunta {i}: ")
    r1 = input("    Respuesta 1: ")
    r2 = input("    Respuesta 2: ")
    r3 = input("    Respuesta 3: ")
    myquestion = Question(exito=True, pregunta=q,
                          respuesta1=r1, respuesta2=r2, respuesta3=r3)
    print("Pregunta guardada")
    f.write(myquestion.getJson() + ',\n')
f.close()
