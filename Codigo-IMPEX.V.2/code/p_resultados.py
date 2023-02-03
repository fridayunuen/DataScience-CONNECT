import impex 
import V_Imagenes as vi
import pandas as pd
import os
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

if len(ItemsNoGenerados) > 0:
    ItemsNoGenerados.to_excel("ItemsNoGenerados.xlsx", index=False)
    print("Revisar ItemsNoGenerados.xlsx")