import os

try:
    pd.read_excel(r'S:\OMNI\HerramientasCode\MappingDiario\Reportes\ProductosGeneradosImpex.xlsx')
    print('Reporte historico existe')
except:
    print('Conecta tu VPN o asegurate que el reporte de ProductosGeneradosImpex.xlsx se encuentre cerrado')
    exit()


import impex 
import V_Imagenes as vi
import pandas as pd

import V_I_ItemsExtraer as vie
import Directory as Dir

Mapping_final = impex.Mapping
Items_generados = Mapping_final[['sku','Lote']]
Items_generados = Items_generados.drop_duplicates(subset=['sku'], keep='first')
Items_generados["sku"] = Items_generados["sku"].astype(str)


ItemsGenerar = pd.read_excel(Dir.carpeta_intupt + '\ItemsGenerar.xlsx')
ItemsGenerar.columns = ['sku']
ItemsGenerar['sku'] = ItemsGenerar['sku'].astype(str)


# joins 
ItemsNoGenerados = ItemsGenerar[~ItemsGenerar['sku'].isin(Items_generados['sku'])]
ItemsNoGenerados = ItemsNoGenerados.reset_index(drop=True)

ItemsGenerados = ItemsGenerar[ItemsGenerar['sku'].isin(Items_generados['sku'])]
ItemsGenerados = ItemsGenerados.merge(Items_generados, on='sku', how='left')
ItemsGenerados = ItemsGenerados.reset_index(drop=True)

os.chdir(Dir.resultados_hoy_reportes)
ItemsGenerados.to_excel("ItemsGenerados.xlsx", index=False)

reporte = ItemsGenerados['sku']
reporte = pd.DataFrame(reporte)
reporte.columns = ['sku']

# get current date and time
from datetime import datetime
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# add column to dataframe with current date and time
reporte.loc[:,'DateUpload'] = dt_string

# get name of user who is running the script
import getpass
user = getpass.getuser()
reporte.loc[:,'Equipo'] = user

historico = pd.read_excel(r'S:\OMNI\HerramientasCode\MappingDiario\Reportes\ProductosGeneradosImpex.xlsx')
historico = pd.concat([historico, reporte], ignore_index=True)
historico.sort_values(by=['DateUpload'], inplace=True, ascending=False)
historico = historico.drop_duplicates(subset=['sku'], keep='first')
historico.to_excel(r'S:\OMNI\HerramientasCode\MappingDiario\Reportes\ProductosGeneradosImpex.xlsx', index=False)

if len(ItemsNoGenerados) > 0:
    ItemsNoGenerados.to_excel("ItemsNoGenerados.xlsx", index=False)
    print("Revisar ItemsNoGenerados.xlsx")