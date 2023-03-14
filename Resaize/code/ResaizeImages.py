import pandas as pd
import os
from PIL import Image
import aux_mapping_items as aux_map

carpeta_code = os.getcwd()
path_input = carpeta_code.replace('code', 'input')
path_output = carpeta_code.replace('code', 'output')

if os.path.exists(path_output) == False:
    os.mkdir(path_output)

try: 
    carpeta_fotos = aux_map.map_files(path_input, 'Mapping.csv')
except:
    print('Recuerda tener el archivo de mapping cerrado')

# corrigienodo path si viene de apple ------------------------------------------------------------------------------------
#carpeta_fotos['path'] = '/'+carpeta_fotos['path'].str.split('/').str[1] 
#carpeta_fotos['filename'] = carpeta_fotos['filename'].str.split('/').str[-1]

# Limpiando  dataframe
carpeta_fotos = carpeta_fotos[carpeta_fotos['sku'] != '0']
carpeta_fotos = carpeta_fotos[carpeta_fotos['sku'] != 0]
carpeta_fotos = carpeta_fotos[carpeta_fotos['suffix'] != 0]
carpeta_fotos = carpeta_fotos.reset_index()

carpeta_fotos['len'] = ''
for i in range(len(carpeta_fotos)):
    filename = carpeta_fotos.loc[i, 'filename']
    carpeta_fotos.loc[i, 'len'] = len(filename)

carpeta_fotos = carpeta_fotos[carpeta_fotos['len'] == 16]

carpeta_fotos

#carpeta_fotos = carpeta_fotos.reset_index(inplace=False)

# corrigienodo path si viene de apple ------------------------------------------------------------------------------------
#carpeta_fotos['path'] = '/'+carpeta_fotos['path'].str.split('/').str[1] 
#carpeta_fotos['filename'] = carpeta_fotos['filename'].str.split('/').str[-1]

# Limpiando  dataframe
carpeta_fotos = carpeta_fotos[carpeta_fotos['sku'] != '0']
carpeta_fotos = carpeta_fotos[carpeta_fotos['sku'] != 0]
carpeta_fotos = carpeta_fotos[carpeta_fotos['suffix'] != 0]
carpeta_fotos = carpeta_fotos.reset_index()

carpeta_fotos['len'] = ''
for i in range(len(carpeta_fotos)):
    filename = carpeta_fotos.loc[i, 'filename']
    carpeta_fotos.loc[i, 'len'] = len(filename)

carpeta_fotos = carpeta_fotos[carpeta_fotos['len'] == 16]

# join width and length
carpeta_fotos["width"] = carpeta_fotos["width"].astype(str)
carpeta_fotos["length"] = carpeta_fotos["length"].astype(str)
carpeta_fotos["width_length"] = carpeta_fotos["width"] + "Wx" + carpeta_fotos["length"]+'H'

carpeta_fotos = carpeta_fotos[(carpeta_fotos['version'] == '0') | (carpeta_fotos['version'] == 0)].reset_index(drop=True)
fotos = carpeta_fotos['key'].unique()

# Detectando errores --------------------------------------------------------------------------------------------------------------
errores = pd.DataFrame(columns=['key', 'tipo_error'])
for foto in fotos:
    df_foto  = carpeta_fotos[carpeta_fotos['key'] == foto]

    if df_foto['type'].unique()[0] != 'jpg':
        error = pd.DataFrame({'key':foto, 'tipo_error':'no es jpg'}, index=[0])
        errores = pd.concat([errores, error])
        print("No es jpg: ", foto)
    
    if '1200Wx1200H' not in df_foto['width_length'].values:
        error = pd.DataFrame({'key':foto, 'tipo_error':'falta tamaño 1200x1200'}, index=[0])
        errores = pd.concat([errores, error])
        print("Falta tamaño 1200x1200 en: ", foto)

    if '400Wx600H' not in df_foto['width_length'].values:
        error = pd.DataFrame({'key':foto, 'tipo_error':'falta tamaño 400x600'}, index=[0])
        errores = pd.concat([errores, error])
        print("Falta tamaño 400x600 en: ", foto)

    
if len(errores) == len(fotos):
    print("Todas las fotos tienen algun error, revise reporte")
    exit()


info_errores = carpeta_fotos[carpeta_fotos['key'].isin(errores['key'])].reset_index(drop=True)

if len(errores) > 0:

    carpeta_error = "errores"
    os.chdir(carpeta_code)

    if not os.path.exists(carpeta_error):
        os.makedirs(carpeta_error)
    try:
        errores.to_excel(carpeta_error+r'\\'+"reporte_errores.xlsx", index=False)
        print("Reporte de errores generado")
    except:
        print("Si quieres visualizar el reporte de errores, cierra el archivo reporte_errores.xlsx")
    
    errores = errores['key'].unique()
    info_errores = carpeta_fotos[carpeta_fotos['key'].isin(errores)].reset_index(drop=True)

carpeta_fotos = carpeta_fotos[(carpeta_fotos['width_length'] == '400Wx600H') | (carpeta_fotos['width_length'] == '1200Wx1200H')]
carpeta_fotos = carpeta_fotos.reset_index(drop = True)

os.chdir(carpeta_code)

def resaize_images(carpeta_fotos, carpeta_nueva, path_fotos):
    if not os.path.exists(carpeta_nueva):
        os.makedirs(carpeta_nueva)

    for i in range(len(carpeta_fotos)):
        path = path_fotos + carpeta_fotos.loc[i, 'path']
        filename = carpeta_fotos.loc[i, 'filename']
        
        width_length = carpeta_fotos.loc[i,'width_length']
        
        os.chdir(path)
        print(filename)
        if width_length == '1200Wx1200H':

            img = Image.open(filename)
            # Cuadrado
            for size in [515, 300, 96, 65, 30, 40]:
                os.chdir(carpeta_nueva)
                img = img.resize((size, size), Image.ANTIALIAS)
                size = str(size)
                file_name = size + 'Wx' + size + 'H_' + carpeta_fotos.loc[i, 'filename']
                img.save(file_name)

                os.chdir(path)
        new_name = os.path.join(carpeta_nueva, width_length + '_' + filename)
        try:
            os.rename(filename, new_name)
        except:
            pass
        
resaize_images(carpeta_fotos, path_output, path_input)

os.chdir(carpeta_code)
subcareptas = os.listdir(path_input)
for subcarepta in subcareptas:

    subcarepta = os.path.join(path_input, subcarepta)
    if os.listdir(subcarepta) == []:
        os.rmdir(subcarepta)


# Analizando todo lo generado ------------------------------------------------------------------------------------
imagenes = os.listdir(path_output)

df = imagenes
df = pd.DataFrame(df)
df.columns = ['Imagenes']
es = df['Imagenes'].str.split('_').str[1].unique()
es = pd.DataFrame(es)

es.columns = ['sku']
os.chdir(carpeta_code)
es.to_excel('items_upload.xlsx', index = False)
print('Proceso concluido con exito')
