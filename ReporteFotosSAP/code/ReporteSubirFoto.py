import os
import pandas as pd

path = os.getcwd()
path_input = path.replace("code", "input")

path_contrasenas = r'C:\Users\fcolin\Desktop\input\CredencialesConnect.json'
path_sap_reporte = r'S:\OMNI\HerramientasCode\MappingDiario\input'
path_code = os.getcwd()
path_output = path_code.replace("code", "output")
# select a file with an interactive dialog
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# select a file with an interactive dialog
Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename_SAP = askopenfilename() # show an "Open" dialog box and return the path to the selected file
# close the dialog
Tk().destroy()
# DRIVE ----------------------------------------------------------------------------------------------
print('Leyendo Drive...')
try:
    Drive = pd.read_csv(r"S:\OMNI\HerramientasCode\MappingDiario\Mapping.csv")
except:
    print('No se puede acceder a la carpeta S:, revise la conexión a la red')
    exit()

Drive.sort_values(by=['creation_date'], ascending=False, inplace=True)
drive = Drive[["sku", "path"]]
drive = drive.drop_duplicates(subset="sku", keep="first")
drive.reset_index(drop=True, inplace=True)
drive["sku"] = drive["sku"].astype(str)
drive
# Producto dado de alta en SAP ------------------------------------------------
print("Leyendo archivo SAP...")
ProductosSAP = pd.read_csv(filename_SAP, sep=";", header=1)
#ProductosSAP = pd.read_csv(path_sap_reporte + "\SAP.csv", sep=";", header=1)
ProductosSAP['code[unique=true]'] = ProductosSAP['code[unique=true]'].str.replace("_", "")

ProductosSAP['len_code'] = ProductosSAP['code[unique=true]'].str.len()
ProductosSAP = ProductosSAP[ProductosSAP['len_code'] == 13]
ProductosSAP['sku'] = ProductosSAP['code[unique=true]'].str[:10]
ProductosSAP.drop_duplicates(subset="sku", keep="first", inplace=True)
ProductosSAP
ProductosSAP[~ProductosSAP['picture(code)[collection-delimiter=|]'].isna()]
# crear una nueva columna en la que si no tiene foto, ponga "Sin foto"
ProductosSAP['SAP'] = ProductosSAP['picture(code)[collection-delimiter=|]'].apply(lambda x: "Sin foto" if pd.isna(x) else "Con foto")

df_sap = ProductosSAP[['sku', 'SAP']]
df_sap

# INVENTARIOS --------------------------------------------------------------------------------------------
print("Leyendo base de datos... extrayendo tallas")
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
df = df[df['SAP'] != 'Con foto']
sin_foto = df[df['path'].isna()]
sin_foto

# fotos que no estan en SAP, necesita crearse un archivo para migrar
migrar = df[(df['SAP'].isna()) & (~df['path'].isna())]
subir = df[(~df['SAP'].isna()) & (~df['path'].isna())]
subir

sin_foto.reset_index(drop=True, inplace=True)
migrar
prod_migrar = migrar['sku'].str[:7].unique()
prod_migrar = pd.DataFrame(prod_migrar)
prod_migrar['E-COMMERCE'] = 'E-COMMERCE'
prod_migrar

#prod_migrar.to_excel(path_output + "\Migrar.xlsx", index=False, header=False)
#sin_foto.to_excel(path_output + "\SinFotoDriveCONNECT.xlsx", index=False)
#subir.to_excel(path_output + "\SubirFoto.xlsx", index=False)

def crear_excel(df, titulo, header=True):
    if df.empty:
        print("No hay productos en" , titulo, " :)")
    else:
        df.to_excel(path_output + titulo , index=False, header=header)
crear_excel(df, "\ReporteFotos.xlsx")
crear_excel(migrar, "\Migrar.xlsx", False)
crear_excel(sin_foto, "\SinFotoDriveCONNECT.xlsx")
crear_excel(subir, "\SubirFoto.xlsx")

print('Proceso terminado con exito :)')