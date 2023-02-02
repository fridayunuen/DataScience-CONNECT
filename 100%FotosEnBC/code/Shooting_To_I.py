import pandas as pd
import os
import numpy as np
import shutil
import json
import os
import aux_mapping_items as aux

dest_file =       r'C:\Users\fcolin\Desktop\input\files'
dir_credenciales = r'C:\Users\fcolin\Desktop\input'
path_drive = r'C:\Users\fcolin\SERVICIOS SHASA S DE RL DE CV\Administrador - Fotografías Subir Pagina'

carpeta_code = os.getcwd()
carpeta_input  =carpeta_code.replace('code', 'input')
carpeta_output =carpeta_code.replace('code', 'output')

def notificacion(titulo, mensaje, tiempo):
    #import time 
    from plyer import notification 

    if __name__ == '__main__':
        notification.notify(
            title=titulo,
            message=mensaje,
            timeout=tiempo
            )

notificacion('Shooting to I', 'Iniciando proceso', 5)

# Fotos en I------------------------------------------------

path_fotos = r'I:'
out_mapping = os.path.join(carpeta_output, 'Mapping_I.csv')
fotos_I = aux.map_files(path_fotos, out_mapping)
fotos_I = fotos_I[fotos_I['sku']!=0]
fotos_I['sku'] = fotos_I['sku'].astype(str)


# Drive de fotografias -------------------------------------
import clean_images_names as clean
clean.rename_images_rarechars(path_drive)

name_drive_csv = os.path.join(carpeta_output, 'Map_Items_Foto_Drive.csv')

df_drive = aux.map_files(path_drive, name_drive_csv)

df_drive['sku'] = df_drive['sku'].astype(str)

def separate_filename_path(string):
    '''
    This function separates the filename and the type_file of a string.
    '''
    string = str(string)
    position_point = string.rfind('.')
    type_file = string[position_point+1:]
    return  type_file

df_drive['type_file'] = df_drive['filename'].apply(lambda x: separate_filename_path(x))

def detect_Wx(string):
    '''
    This function detects if there is a Wx in the filename.
    '''
    string = str(string)
    if 'Wx' in string:        
        position_Wx = string.find('Wx')
        size = int(string[:position_Wx])
        return  size
    else:
        return 0


df_drive['size'] = df_drive['filename'].apply(lambda x: detect_Wx(x))

        
# solo se van a aceptar formatos jpg y jpeg porque son los unicos que acepta BC
df_drive = df_drive[(df_drive['type_file']=='jpg') | (df_drive['type_file']=='jpeg')]

# Filtrandoy ordenando
df_drive = df_drive.sort_values(by=['suffix'], ascending=True)
df_drive = df_drive.sort_values(by=['creation_date', 'key', 'filename'], ascending=False)
df_drive = df_drive[(df_drive['suffix'] == '0') | (df_drive['suffix'] == '1')]
df_drive = df_drive.sort_values(by=['size'], ascending=False)
df_drive = df_drive.drop_duplicates(subset=['sku'], keep='first')
df_drive.columns = df_drive.columns + '_drive'


# Conexxion ------------------------------------------------
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
SELECT DISTINCT [Original Vendor Item No_] AS [sku], [Original Vendor Item No_], [Item], [Division Code]   ,[Description]
FROM [Allocations].[dbo].[Item_BC]
LEFT JOIN [SH_Reports].[dbo].[Imagenes_File]
ON SUBSTRING([Item] COLLATE SQL_Latin1_General_CP1_CI_AS , 1, 7) = [Original Vendor Item No_]
WHERE [No_] != ''  AND [Division Code] NOT IN ('INSUMOS') 

UNION ALL

SELECT [No_], [Original Vendor Item No_] AS [sku], [Item], [Division Code]   ,[Description]
FROM [Allocations].[dbo].[Item_BC]

LEFT JOIN [SH_Reports].[dbo].[Imagenes_File]
ON SUBSTRING([Item] COLLATE SQL_Latin1_General_CP1_CI_AS , 1, 7) = [No_]

WHERE [No_] != ''  AND [Division Code] NOT IN ('INSUMOS') 

'''

df_items = pd.read_sql_query(query_items_foto, conn)

df_items = df_items[df_items['Item'].isnull()]
df_items['sku'] = df_items['sku'].astype(str)
df_items = df_items[df_items['Division Code'] != 'INSUMOS']

# Items que si tienen foto en el drive

df_items_clones = pd.merge(df_items, df_drive, left_on='sku', right_on='sku_drive', how='left')

# Fotos en I------------------------------------------------
#os.chdir('out')
#fotos_I = pd.read_csv('Mapping.csv')
#os.chdir('..')
#fotos_I = fotos_I[fotos_I['sku']!=0]
#fotos_I['sku'] = fotos_I['sku'].astype(str)

#df_drive = aux.map_files(path_drive, 'Map_Items_Foto.csv')
#df_drive['sku'] = df_drive['sku'].astype(str)

# Items que si tienen foto en el drive
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

# Equivalencias de Division code con la caprta en la que se va a colocar 

equiv = pd.read_excel(os.path.join(carpeta_input, 'equivalencia_carpeta.xlsx'))
df_items_mover = pd.merge(df_items_mover, equiv, on='Division Code', how='left')

# Si existen fotos en la carpeta pero no estan en BC tal vez sea por que no se acepta el formato o algo parecido
# Entces si ya tenemos una foto de shooting se elimina lo que este en la carpeta I 

#df_items_mover = pd.merge(df_items_mover, fotos_I, on='sku', how='left')
fotos_I.columns = fotos_I.columns + '_I'
df_items_mover = pd.merge(df_items_mover, fotos_I, left_on='sku', right_on='sku_I', how='left')

# Preparamos para comenzar a mover las fotos

'''fotos_eliminar = df_items_mover[~df_items_mover['filename_I'].isna()]
if fotos_eliminar.shape[0] > 0:
    fotos_eliminar.drop_duplicates(subset=['filename_I'], keep='first', inplace=True)
    fotos_eliminar.reset_index(inplace=True, drop=True)
    # replace nan with ''
    fotos_eliminar['path'] = fotos_eliminar['path_I'].replace(np.nan, '', regex=True)
    for i in fotos_eliminar.index:
        path = path_fotos + fotos_eliminar.loc[i, 'path_I']  + fotos_eliminar.loc[i, 'filename_I']
        os.remove(path)'''

df_items_mover = df_items_mover[~df_items_mover['Carpeta'].isna()]
df_items_mover = df_items_mover[df_items_mover['filename_I'].isna()] ###### --------------

df_items_mover.drop_duplicates(subset=['sku'], keep='first', inplace=True)
df_items_mover.sort_values(by=['creation_date_drive'], ascending=False, inplace=True)

df_items_mover.reset_index(inplace=True, drop=True)

item_generados = []
errores = []

print('Realizando una copia de las fotos de Shooting hacia I:')
for i in df_items_mover.index:

    new_name = os.path.join(df_items_mover.loc[i,'Carpeta'], df_items_mover.loc[i,'sku'] + '.jpg')
    new_name = os.path.join(path_fotos, new_name)

    old_name = os.path.join(df_items_mover.loc[i,'path_drive'], df_items_mover.loc[i,'filename_drive'])
    old_name = path_drive+old_name
    
    try: 
        shutil.copy(old_name, new_name)
        #print(df_items_mover.loc[i,'sku'])
        item_generados.append(df_items_mover.loc[i,'sku'])
    except:
        print('Error: ' + df_items_mover.loc[i,'sku'])
        errores.append(df_items_mover.loc[i,'filename_drive'])

    #print(old_name)
    #print(new_name)
if len(item_generados) > 0:
    item_generados = pd.DataFrame(item_generados, columns=['sku'])
    items_detalles = df_items_mover[['Original Vendor Item No_', 'sku', 'Description' ,'Division Code', 'Carpeta', 'filename_drive', 'path_drive']]
    item_generados = pd.merge(item_generados, items_detalles, on='sku', how='left')
    item_generados.to_excel(os.path.join(carpeta_output, 'items_generados.xlsx'), index=False)

    import C003_enviar_correo as correo

    Destinatarios = pd.read_excel(os.path.join(dest_file, "Destinatarios_Shooting_I.xlsx"), index_col=0)
    Destinatarios = list(Destinatarios.index)
    Destinatarios = ";".join(Destinatarios)
    correo.enviar_correo(Destinatarios ,subject='Imagenes nuevas en I:', body='Imagenes shooting a la carpeta I:', attachment=carpeta_output + '\items_generados.xlsx')

if len(errores) > 0:
    errores = pd.DataFrame(errores, columns=['filename_drive'])
    errores.to_excel(os.path.join(carpeta_output, 'errores.xlsx'), index=False)

    import C003_enviar_correo as correo

    Destinatarios = pd.read_excel(os.path.join(dest_file, "MiCorreo.xlsx"), index_col=0)
    Destinatarios = list(Destinatarios.index)
    Destinatarios = ";".join(Destinatarios)
    correo.enviar_correo(Destinatarios,subject='Errores al pasar imagenes de shooitng a I', body='', attachment=carpeta_output +'\errores.xlsx')


print('Poroceso terminado con exito')   
notificacion('Shooting to I', 'Poroceso terminado con exito', 5) 