import os
import pandas as pd
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import aux_mapping_items as aux



path = os.getcwd()
path_input = path.replace("code", "input")

path_contrasenas = r'C:\Users\fcolin\Desktop\input\CredencialesConnect.json'
#path_sap_reporte = r'S:\OMNI\HerramientasCode\MappingDiario\input'
path_code = os.getcwd()
path_output = path_code.replace("code", "output")


# Producto dado de alta en SAP ------------------------------------------------
print("Leyendo archivo SAP...")

Tk().withdraw() 
filename_SAP = askopenfilename() 
Tk().destroy()
time.sleep(5)

ProductosSAP = pd.read_csv(filename_SAP, sep=";", header=0)

ProductosSAP['code[unique=true]'] = ProductosSAP['code[unique=true]'].str.replace("_", "")
ProductosSAP['len_code'] = ProductosSAP['code[unique=true]'].str.len()

#ProductosSAP[ProductosSAP['sku'] == '2109645051']
ProductosSAP

ProductosSAP['sku'] = ProductosSAP['code[unique=true]'].str[:10]

# Vamos a detectar los productos que tienen 10 digitos
dig10 = ProductosSAP[['sku', 'len_code']]
dig10 = dig10.sort_values(by=['len_code'], ascending=False)
dig10 = dig10.drop_duplicates(subset="sku", keep="first")
dig10 = dig10[dig10['len_code'] == 10]
dig10


dig10.drop_duplicates(subset="sku", keep="first")
#dig10 = dig10[dig10['len_code'] == 10]
dig10['len_code'].value_counts()


ProductosSAP = ProductosSAP[ProductosSAP['len_code'] == 13]

ProductosSAP.drop_duplicates(subset="sku", keep="first", inplace=True)
ProductosSAP
ProductosSAP[~ProductosSAP['picture(code)[collection-delimiter=|]'].isna()]
# crear una nueva columna en la que si no tiene foto, ponga "Sin foto"
ProductosSAP['SAP'] = ProductosSAP['picture(code)[collection-delimiter=|]'].apply(lambda x: "Sin foto" if pd.isna(x) else "Con foto")
df_sap = ProductosSAP[['sku', 'SAP']]
df_sap



# DRIVE ---------------------------------------------------------------------------
print('Leyendo Drive...')
#Drive = pd.read_csv(r"S:\OMNI\HerramientasCode\MappingDiario\Mapping.csv")

path_fotos = r'C:\Users\fcolin\OneDrive - SERVICIOS SHASA S DE RL DE CV\CONNECT'
nom_items_mapping = os.path.join(path_output, 'Mapping.csv')
Drive = aux.map_files(path_fotos, saveas=nom_items_mapping)
Drive.sort_values(by=['creation_date'], ascending=False, inplace=True)

drive = Drive[["sku", "path"]]
drive = drive.drop_duplicates(subset="sku", keep="first")
drive.reset_index(drop=True, inplace=True)
drive["sku"] = drive["sku"].astype(str)
drive


# INVENTARIOS --------------------------------------------------------------------------------------------
print("Leyendo base de datos... ")
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
import json

with open(path_contrasenas) as f:
    credenciales = json.load(f)

try: 
    connection_string = 'DRIVER={SQL Server};SERVER=Shjet-prod;DATABASE=Allocations;UID='+ credenciales['usuario'] +';PWD='+credenciales['password']
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = create_engine(connection_url)
    conn = engine.connect()
except:
    print("Base de datos en mantenimiento")
    exit()
    
query = '''
SELECT  CONCAT([Item No_] ,[Cod_Color]) AS sku
     ,[Division Code]
     ,[Status Code] 
     ,SUM([Inv_E002]) AS [Inv_E002]
     ,SUM([Inv_TransE002]) AS [Inv_TransE002]
     ,SUM([ODS]) AS [ODS] 
     ,SUM([Qtty Pen]) AS [Qtty Pen]
       
  FROM [Flash_BC].[dbo].[PP_Shasacom]
  WHERE [Color] IS NOT NULL 
  AND [Item Category Code] != 'CANDY'
  GROUP BY CONCAT([Item No_] ,[Cod_Color])
     ,[Division Code]
      ,[Item Category Code]
      ,[Product Group Code]
      ,[Oferta]
      ,[Status Code]  
 '''
df_query = pd.read_sql_query(query, conn)
# sustituir los valores nulos por 0
df_query['Qtty Pen'].fillna(0, inplace=True)
# las qtty pen de joyeria deben ser 0 si el status es VAN
df_query.loc[(df_query['Qtty Pen']>0) & (df_query["Division Code"] == "M-JEW")& (df_query["Status Code"] == "VAN"), 'Qtty Pen'] = 0
df_query.loc[(df_query['Qtty Pen']>0) & (df_query["Division Code"] == "W-JEW")& (df_query["Status Code"] == "VAN"), 'Qtty Pen'] = 0
df_query = df_query[['sku', 'Inv_E002', 'Inv_TransE002','ODS', 'Qtty Pen']]
df_query.index = df_query['sku']
df_query.drop('sku', axis=1, inplace=True)
# substitute nan values with 0
df_query.fillna(0, inplace=True)
# substitute negative values with 0
df_query[df_query < 0] = 0
# Sumando todas las columnas
df_query['Total'] = df_query.sum(axis=1)
# Seleccionando solo los productos con un total mayor a 0 
df_query = df_query[df_query['Total']>0]
df_query.reset_index(inplace=True)

df = pd.merge(df_query, df_sap, on="sku", how="left")

df['Total'].fillna(0, inplace=True)
df['Total'] = df['Total'].astype(int)
df = df[df['Total']>0]
df = pd.merge(df, drive, on="sku", how="left")
df
df[df['sku'].isin(dig10['sku'])] # Productos con inventario a 10 digitos
if len(dig10)>0:
    df = df[~df['sku'].isin(dig10['sku'])]
df['Padre'] = df['sku'].str[:7]

migrar = df[(df['SAP'].isna()) & (~df['path'].isna())]
migrar.drop_duplicates(subset="Padre", keep="first")

prod_migrar = migrar['Padre'].str[:7].unique()
prod_migrar = pd.DataFrame(prod_migrar)
prod_migrar['E-COMMERCE'] = 'E-COMMERCE'
prod_migrar.columns = ['sku', 'E-COMMERCE']

# elimniar de prod migrar si sku esta en df_sap
prod_migrar = prod_migrar[~prod_migrar['sku'].isin(df_sap['sku'].str[:7])]
# Dado de alta en SAP sin foto en Drive
sin_foto = df[(df['SAP'] == 'Sin foto') & (df['path'].isna())] 

# Fotos listas para subir a SAP
subir = df[(df['SAP'] == 'Sin foto') & (~df['path'].isna())] 

# Fotos para subir a BC
prod_migrar
def crear_excel(df, titulo, header=True):
    if df.empty:
        print("No hay productos en" , titulo)
    else:
        df.to_excel(path_output + titulo , index=False, header=header)

crear_excel(df, "\ReporteFotos.xlsx")
crear_excel(prod_migrar, "\Migrar.xlsx", False)
crear_excel(sin_foto, "\SinFotoDriveCONNECT.xlsx")
crear_excel(subir, "\SubirFoto.xlsx")

print('Proceso terminado con exito :)')
