import getopt
import sys
from os import listdir
from os.path import isfile, join
import router
import colorama

colorama.init(autoreset=True)


def printhelp():
    help = ('\nArgumentos:' +
            '\n    -h, --help:                   Imprime esta ayuda' +
            '\n    -i ARCHIVO' +
            '\n       --ifile=ARCHIVO            Analiza el archivo en busca de respuestas' +
            '\n    --inputfolder=CARPETA         Analiza todos los archivos en la carpeta' +
            '\n    -a, --auto                    Modo autonomo')
    print(help)
    sys.exit()


def main(argv):
    print("Bienvenido al confettibot!")
    try:
        opts, args = getopt.getopt(
            argv, "hai:", ["help", "ifile=", "auto", "inputfolder="])
    except getopt.GetoptError:
        printhelp()

    if len(opts) == 0:
        printhelp()

    for opt, arg in opts:
        if opt is None:
            printhelp()
        elif opt in ('-h', "--help"):
            printhelp()
        elif opt in ("-i", "--ifile"):
            router.singleFile(arg)
        elif opt == "--inputfolder":
            router.allInFolder(arg)
        elif opt in ("-a", "--auto"):
            router.autonomousMode()
