import os
import pandas as pd

path = os.getcwd()
path_input = path.replace("code", "input")
path_output = r'S:\OMNI\HerramientasCode\MappingDiario'
path_contrasenas = r'C:\Users\fcolin\Desktop\input\CredencialesConnect.json'
path_sap_reporte = r'S:\OMNI\HerramientasCode\MappingDiario\input'

# DRIVE ----------------------------------------------------------------------------------------------
Drive = pd.read_csv(r"S:\OMNI\HerramientasCode\MappingDiario\Mapping.csv")
Drive.sort_values(by=['creation_date'], ascending=False, inplace=True)
drive = Drive[["sku", "path"]]
drive = drive.drop_duplicates(subset="sku", keep="first")
drive.reset_index(drop=True, inplace=True)
drive["sku"] = drive["sku"].astype(str)

# Producto dado de alta en SAP ------------------------------------------------
ProductosSAP = pd.read_csv(path_sap_reporte + "\SAP.csv", sep=";", header=1)
ProductosSAP["sku"] = (ProductosSAP["code[unique=true]"].str[:7]+ProductosSAP["code[unique=true]"].str[8:]).str[:10].astype(str)
ProductosSAP = ProductosSAP.drop_duplicates(subset="sku", keep="first")

df_sap = ProductosSAP[ProductosSAP['picture(code)[collection-delimiter=|]'].isna()]
df_sap.loc[:,'SAP'] = 'SinFoto'
df_sap = df_sap[['sku', 'SAP']]
df_sap.reset_index(drop=True, inplace=True)
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

# UNION ----------------------------------------------------------------------------------------------
df = pd.merge(df_sap, df_query, on="sku", how="left")
df['Total'].fillna(0, inplace=True)
df['Total'] = df['Total'].astype(int)
df = df[df['Total']>0]
df = pd.merge(df, drive, on="sku", how="left")
df.to_excel(path_output + "\ProductosSinFoto.xlsx", index=False)

print('Proceso terminado con exito....')