from enum import unique
import pandas as pd
from PIL import Image
import zipfile
import os

#from zmq import EVENT_CLOSE_FAILED

import V_I_Cubo as ivc
import Directory as Dir

# 2. Extrayendo los productos validos a la carpeta de resultados del dia y hora actual
os.chdir(Dir.carpeta_intupt)

path_fotos = open('path.txt', 'r').readline()
#Mapping = pd.read_csv('Mapping.csv')
Mapping = pd.read_csv('S:\OMNI\HerramientasCode\MappingDiario\Mapping.csv')


os.chdir(path_fotos)

col = Mapping.columns                                                                                                                                                                                                                                                  
map = pd.DataFrame(columns=col)
for item in ivc.item:
    item = int(item)
    df = Mapping[Mapping['sku'] == item]
    map = pd.concat([map, df])    

map.index = range(len(map))

Mapping = map

necesario1 = ["1200",  "300","400", "515", "65", "96"]
necesario2 = ["1200",  "300","600", "515", "65", "96"]

#necesario1 = ["1200","400", "515", "65", "96"]
#necesario2 = ["1200","600", "515", "65", "96"]


imagenes_nombre = Mapping['filename']

Mapping["W"] = ''
Mapping["H"] = ''
for imagen in imagenes_nombre:
    W = imagen[0:imagen.find("W")]
    H = imagen[imagen.find("W")+2:imagen.find("H")]
    Mapping.loc[Mapping['filename'] == imagen, 'W'] = W
    Mapping.loc[Mapping['filename'] == imagen, 'H'] = H

    if W in necesario1 and H in necesario2:
        pass
    else:
        print("Eliminando del mapping " + imagen)
        if imagen in Mapping['filename'].values:
            Mapping.drop(Mapping[Mapping['filename'] == imagen].index, inplace=True)


tamanos_faltantes = []
# Detectando que esten las imagenes de todas los tamanos necesarios
for sku in Mapping['sku'].unique():
    df = Mapping[Mapping['sku'] == sku]
    sufijo = df["suffix"].unique()

    for suf in sufijo:
        df1 = df[df['suffix'] == suf]
        W = df1["W"].values
        H = df1["H"].values
        
        # detect if the list contains all the elements of the list
        if all(elem in W for elem in necesario1) and all(elem in H for elem in necesario2):
           pass
        else:
            tamanos_faltantes.append(sku)
        
        
# delete duplicates from a list
tamanos_faltantes = list(dict.fromkeys(tamanos_faltantes))


if tamanos_faltantes != []:
    print("Los siguientes productos no tienen todos los tamaños necesarios")
    print(tamanos_faltantes)
    os.chdir(Dir.resultados_hoy_reportes)
    pd.DataFrame(tamanos_faltantes).to_excel("tamanos_faltantes.xlsx", index=False)



    for item in tamanos_faltantes:
        Mapping = Mapping[Mapping['sku'] != item]

print("Cantidad de productos validos: " + str(len(Mapping['sku'].unique())))

# Enviando los productos a un zip

os.chdir(path_fotos)

# get user name of the current system
user = os.getlogin()

print("Descargando imagenes y preparando zip... ")


zip_nombre = user + "_imagenes.zip"


if len(Mapping['filename']) == 0:
    print("No hay productos validos")
    exit()


for imagen in Mapping['filename']:
    with zipfile.ZipFile(zip_nombre, 'a') as zip:

        try:
            zip.write(imagen)
        except:
            print("No se pudo agregar " + imagen)
            pass

# 3. Enviando el zip a la carpeta de resultados
print("Enviando zip a la carpeta de resultados... ")

os.rename(zip_nombre, Dir.resultados_hoy + "\\" + zip_nombre)

#unzip the file
with zipfile.ZipFile(Dir.resultados_hoy + "\\" + zip_nombre, 'r') as zip_ref:
    zip_ref.extractall(Dir.resultados_hoy)

# delete the zip file
os.remove(Dir.resultados_hoy + "\\" + zip_nombre)

# 4. Creando lotes de imagenes de acuerdo a sus bytes
os.chdir(Dir.resultados_hoy)

# get size of the file in bytesfrom Mapping['filename']
def get_size(file):
    return os.path.getsize(file)

# get the size of the file in bytes
Mapping['size'] = Mapping['filename'].apply(get_size)

# group by sku and sum the size of the files
sizes = Mapping.groupby(['sku'], as_index=False)['size'].sum()

# now we gonna create the batches
# the size of the batch is 32 MB
# the size of the batch is 32000000 bytes

# create a new function wich agrupate the files by size until the size of the batch is 32 MB

print("Creando lotes de 32 megas...")
r = 1
sizes["Lote"] = ''
sum_size = []

for i in range(len(sizes)):
    size =  sizes['size'][i]
    if sum(sum_size) + size < 32000000:
        sum_size.append(size)
        sizes.loc[i, 'Lote'] = r

    else:
        r += 1
        sum_size = []
        sum_size.append(size) 
        sizes.loc[i, 'Lote'] = r

print("Cantidad de lotes creados: " + str(r))  

# create a new column in the mapping with the batch number
Mapping = pd.merge(Mapping, sizes, on='sku', how='left')

# create the folders
for i in (range(1,r+1)):
    os.mkdir("Lote"+str(i))

# move the files to the folders
for i in range(len(Mapping)):
    file = Mapping['filename'][i]
    lote = Mapping['Lote'][i]

    # os.rename(file, "Lote"+str(lote)+"\\"+file)

    name_zip = "Lote"+str(lote)

    # send to a zip
    with zipfile.ZipFile(name_zip + ".zip", 'a') as zip:
        zip.write(file)

    # delete the file
    os.remove(file)    

# 5. Enviando los lotes a la carpeta de resultados

for i in (range(1,r+1)):
    #name_zip = "ZIP.zip"
    name_zip = "Lote"+str(i)+".zip"
    name_carpet = "Lote"+str(i)

    os.rename(name_zip, Dir.resultados_hoy +"\\"+ name_carpet +"\\" + "ZIP.zip")

