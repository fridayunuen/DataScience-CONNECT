import os
import Directory as Dir
import pandas as pd 

import V_I_ItemsExtraer as iv

from sqlalchemy.engine import URL
from sqlalchemy import create_engine


# Verificacion:
# 1. Verificar que el archivo de entrada exista
# 2. Existan archivos en la localizacion que nos importa
# 3. Exitse la columna Items Variant
# 4. Crice entre tallas Cubo y ItemsGenerar
# 5. Algun producto no existe en Cubo

# 1 
'''if os.path.exists(Dir.carpeta_intupt + '\Cubo.xlsx'):
    
    input = pd.read_excel(Dir.carpeta_intupt + '\Cubo.xlsx')
else:
    print("No existe el archivo Cubo.xlsx en la carpeta input")
    exit()
# 2
cubo = input.iloc[18:,0]
if cubo is None:
    print("El archivo Cubo.xlsx no tiene información")
    exit()

# 3
if cubo.values[0] != 'Item Variant':
    print("El archivo Cubo.xlsx no tiene la columna 'Item Variant' i.e diferente formato")
    exit()

# Cubo & ItemsGenerar -----------------------------------------------------

# 4
tallas_cubo = cubo[1:]
productos = tallas_cubo.str[:10]
cubo = pd.DataFrame({'talla': tallas_cubo, 'producto': productos})

tallas = []
No_Cubo = []
item = []
for i in range(len(iv.inner)):
    p = cubo[cubo['producto'] == iv.inner[i]]
    p = p['talla']
   
    if p.empty:
        print(" --- El producto " + iv.inner[i] + " no tiene tallas en el cubo")
        No_Cubo.append(iv.inner[i])
    else:
        tallas.extend(p.values)
        item.append(iv.inner[i])

if tallas is None:
    print("-- Ninguno de los productos se encuentra en Cubo.xlsx")
    exit()

# 5
if len(No_Cubo) > 0:
    print("--- Existen productos que no se encuentran en Cubo.xlsx, revise carpeta output")
    No_Cubo = pd.DataFrame(No_Cubo, columns=['sku'], index=None)
    os.chdir(Dir.resultados_hoy_reportes)
    No_Cubo.to_excel('NoCubo.xlsx', index=False)
    os.chdir(Dir.code)'''

print("Leyendo base de datos... extrayendo tallas")
import json
with open(r'C:\Users\fcolin\Desktop\input\CredencialesConnect.json') as f:
    credenciales = json.load(f)

connection_string = 'DRIVER={SQL Server};SERVER=Shjet-prod;DATABASE=Allocations;UID='+ credenciales['usuario'] +';PWD='+credenciales['password']
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url)
conn = engine.connect()

# query to get the data
#query = '''SELECT  [Original Vendor Item No_]
#      ,[No_]
#      ,[Variant Code]
#      --,[Date Created]
#  FROM [Allocations].[dbo].[Item_BC_v2]'''


query = '''
SELECT 
 [Item No_] AS [Original Vendor Item No_]
,[Item No_] AS [No_]
,[Variant Code] AS [Variant Code]
FROM [Flash_BC].[dbo].[PP_Shasacom]
WHERE LEN([Item No_]) = 7 
ORDER BY [Item No_] DESC'''


# create a dataframe with the query
try:

    df_query_items = pd.read_sql_query(query, conn)

    # order by date
    #df_query_items = df_query_items.sort_values(by=['Date Created'], ascending=False)


    df_query_items['sku'] = ''
    for index, row in df_query_items.iterrows():
        
        clon = df_query_items.loc[index,"No_"]
        padre = df_query_items.loc[index,"Original Vendor Item No_"]

        if clon == '':
            
            df_query_items.loc[index,'sku']= padre
            
        else:
            df_query_items.loc[index,'sku'] = clon 

    # first three characters of the string
    df_query_items['Variant1'] = df_query_items['Variant Code'].str[:3]
    df_query_items['Variant2'] = df_query_items['Variant Code'].str[3:6]

    df_query_items["VarianteColor"] =  df_query_items['sku']+ df_query_items['Variant1']
    df_query_items["VarianteColorTalla"]=df_query_items["VarianteColor"]+df_query_items['Variant2']

    # reiniciar index
    df_query_items = df_query_items.reset_index(drop=True)
    cubo = df_query_items[["VarianteColor","VarianteColorTalla"]].reindex()
    cubo.columns = ['producto', 'talla']

    tallas = []
    No_Cubo = []
    item = []

    for i in range(len(iv.inner)):
        p = cubo[cubo['producto'] == iv.inner[i]]
        p = p['talla']
    
        if p.empty:
            print(" --- El producto " + iv.inner[i] + " no tiene tallas BC")
            No_Cubo.append(iv.inner[i])
        else:
            tallas.extend(p.values)
            item.append(iv.inner[i])

    if tallas is None:
        print("-- Ninguno de los productos se encuentra en Cubo.xlsx")
        exit()

    # 5
    if len(No_Cubo) > 0:
        print("--- Existen productos que no se encuentran en Cubo.xlsx, revise carpeta output")
        No_Cubo = pd.DataFrame(No_Cubo, columns=['sku'], index=None)
        os.chdir(Dir.resultados_hoy_reportes)
        No_Cubo.to_excel('NoCubo.xlsx', index=False)
        os.chdir(Dir.code)
except:
    print("Error en la consulta, la base de datos se esta actualizando.... intente mas tarde")        
    exit()