# INPUTS ---------------------------------------------------------------------
import aux_mapping_items as aux
import os
import pandas as pd
import shutil
import json 

path_drive = r'C:\Users\fcolin\SERVICIOS SHASA S DE RL DE CV\Administrador - Fotografías Subir Pagina'
dir_credenciales = r'C:\Users\fcolin\Desktop\input'

carpeta_code = os.getcwd()
carpeta_input  =carpeta_code.replace('code', 'input')
carpeta_output =carpeta_code.replace('code', 'output')

# CARPETA I -------------------------------------------------------------
carpetaI = aux.map_files(r'I://', os.path.join(carpeta_output, 'Mapping_I.csv'))
carpetaI = carpetaI[(carpetaI['type'] == 'jpg') | (carpetaI['type'] == 'JPG')]
carpetaI = carpetaI[carpetaI['sku'] != '0']

# Esto se puede sustitur con un where in ?
carpetaI = carpetaI[(carpetaI['path'] == 'CLO') | (carpetaI['path'] == 'ACC')| (carpetaI['path'] == 'SHO') | (carpetaI['path'] == 'BEAUTY') | (carpetaI['path'] == 'JEW')]

# DRIVE -------------------------------------------------------------------

name_drive_csv = os.path.join(carpeta_output, 'Map_Items_Foto_Drive.csv')

df_drive = aux.map_files(path_drive, name_drive_csv)
df_drive['sku'] = df_drive['sku'].astype(str)

def separate_filename_path(string):

    string = str(string)
    position_point = string.rfind('.')
    type_file = string[position_point+1:]
    return  type_file

df_drive['type_file'] = df_drive['filename'].apply(lambda x: separate_filename_path(x))

def detect_Wx(string):
    string = str(string)
    if 'Wx' in string:        
        position_Wx = string.find('Wx')
        size = int(string[:position_Wx])
        return  size
    else:
        return 0

df_drive['SIZE'] = df_drive['filename'].apply(lambda x: detect_Wx(x))
df_drive = df_drive[(df_drive['type_file']=='jpg')]

# Filtrandoy ordenando
df_drive = df_drive.sort_values(by=['suffix'], ascending=True)
df_drive = df_drive.sort_values(by=['creation_date', 'key', 'filename'], ascending=False)
df_drive = df_drive[(df_drive['suffix'] == '0') | (df_drive['suffix'] == '1')]
df_drive = df_drive.sort_values(by=['SIZE'], ascending=False)
df_drive = df_drive.drop_duplicates(subset=['sku'], keep='first')
df_drive.columns = df_drive.columns + '_drive'


# Conexxion --------------------------------------------------------------
# Lo vamos a ultizar paraz remplazar tambien los clones
print('Agregando descripcion del producto...')

credenciales = os.path.join(dir_credenciales, 'Credenciales.json')

with open(credenciales) as f:
    credenciales = json.load(f)

from sqlalchemy.engine import URL
from sqlalchemy import create_engine

connection_string = 'DRIVER={SQL Server};SERVER=Shjet-prod;DATABASE=Allocations;UID='+ credenciales['usuario'] +';PWD='+credenciales['password']
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url)
conn = engine.connect()

query_items_foto = '''
SELECT DISTINCT [Original Vendor Item No_] AS [sku], [Original Vendor Item No_]
FROM [Allocations].[dbo].[Item_BC_v2]
WHERE [No_] != ''  AND [Division Code] NOT IN ('INSUMOS') 

UNION ALL

SELECT [No_], [Original Vendor Item No_] AS [sku]
FROM [Allocations].[dbo].[Item_BC_v2]
WHERE [No_] != ''  AND [Division Code] NOT IN ('INSUMOS') 
'''
df_items = pd.read_sql_query(query_items_foto, conn)

# Clones proccess --------------------------------------------------------
df_items_clones = pd.merge(df_items, df_drive, left_on='sku', right_on='sku_drive', how='left')

df_items['sku'] = df_items['sku'].astype(str)

# Se va a realizar este proceso para los items que no tengan foto con un clon
si_foto = df_items_clones[~df_items_clones['filename_drive'].isna()] #total: 101,269  # no hay: 69,449
no_foto = df_items_clones[df_items_clones['filename_drive'].isna()] 

drive_columns = df_drive.columns.to_list()
no_foto = no_foto.drop(columns=drive_columns)

drive_columns.append('Original Vendor Item No_')
#drive_columns.append('sku')

si_foto = si_foto[drive_columns]

df_items_padres = pd.merge(no_foto, si_foto, on='Original Vendor Item No_', how='left')
df_items_padres = df_items_padres[~df_items_padres['filename_drive'].isna()]

# Dataframe final
si_foto = df_items_clones[~df_items_clones['filename_drive'].isna()] 
df_items_mover = pd.concat([si_foto, df_items_padres])
df_items_mover.reset_index(inplace=True, drop=True)

# Merge -------------------------------------------------------------------
df = pd.merge(carpetaI, df_items_mover, how='left', on = 'sku') #445797 
#Seleccionando solo las imagenes que tambien existen en el drive
df = df[~df['path_drive'].isna()]
# Si los tamaños son diferentes lo mas probable es que sea una imagen diferente
df = df[df['size'] != df['size_drive']]
# order by fecha de creacion
df = df.sort_values(by=['creation_date_drive'], ascending=False)
df.drop_duplicates(subset=['sku'], keep='first', inplace=True)
df.reset_index(inplace=True, drop=True)

# ahora se van a mover las imagenes en el drive hacia la carpeta I
# para que se suban a BC

for i in range(len(df)):
    print('Realizando copia del producto: ', df['sku'][i])
    old_name = path_drive+ df['path_drive'][i]
    old_name = os.path.join(old_name, df['filename_drive'][i])
    #if os.path.exists(old_name):
    new_name = os.path.join(r'I:\\', df['path'][i])
    new_name = os.path.join(new_name, df['filename'][i])
    try: 

        shutil.copy(old_name, new_name)
    except:
        print('Error al mover la imagen: ', old_name, ' a ', new_name)
        continue