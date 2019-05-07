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
            '\n    -a, --auto                    Modo autonomo' +
            '\n    --write-json=CARPETA         Analiza todos los archivos en la carpeta y guarda los datos en un archivo JSON' +
            '\n    --inputfolder=ARCHIVO         Analiza estadisticamente el archivo JSON senalado')
    print(help)
    sys.exit()


def main(argv):
    print("Bienvenido al confettibot!")
    try:
        opts, args = getopt.getopt(
            argv, "hadis:", ["help", "ifile=", "auto", "daemon", "inputfolder=", "write-json=", "read-json="])
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
        elif opt in ("-d", "--daemon"):
            router.autonomousMode()
        elif opt == "--write-json":
            router.writeToFile(arg)
        elif opt == "--read-json":
            router.analyzeJSONFile(arg)


if __name__ == "__main__":
    main(sys.argv[1:])
