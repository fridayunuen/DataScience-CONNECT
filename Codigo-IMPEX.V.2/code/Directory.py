import os
from datetime import datetime

code = os.getcwd()
carpeta = code[:code.find("\code")]

carpeta_intupt = os.path.join(carpeta + '\input')
carpeta_output = os.path.join(carpeta + '\output')
if not os.path.exists(carpeta_output):
    os.makedirs(carpeta_output)

carpeta_resultados = os.path.join(carpeta_output+ '\Resultados')

if not os.path.exists(carpeta_resultados):
    os.makedirs(carpeta_resultados)

now = datetime.now()
dt_string = now.strftime("%d-%m-%Y(%H-%M-%S)")

resultados_hoy = os.path.join(carpeta_resultados, dt_string)
os.makedirs(resultados_hoy)

resultados_hoy_reportes = os.path.join(carpeta_resultados, dt_string,"Reportes")
os.makedirs(resultados_hoy_reportes)
