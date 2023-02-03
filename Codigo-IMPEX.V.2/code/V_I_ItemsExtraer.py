import pandas as pd
import Directory as Dir
import os
import time

# Verificacion:
# 1. Verificar que el archivo de entrada exista
# 2. Solo contiene una columna
# 3. La columna se llama VarianteColor
# 4. La columna no tiene valores nulos
# 5. La columna solo tiene valores numericos
# 6. Los valores de la columna tienen 10 digitos
# 7. Se seleccionan solo los valores unicos
# 8. Existe el archivo mapping.csv, si es así muestra en pantalla la fecha de actualizacion 
# 9. Se compara los archivos items con mapping y excel 

# ItemsGenerar ---------------------------------------------------------------

# 1
if os.path.exists(Dir.carpeta_intupt + '\ItemsGenerar.xlsx'):
    input = pd.read_excel(Dir.carpeta_intupt + '\ItemsGenerar.xlsx')
else:
    print("No existe el archivo ItemsGenerar.xlsx en la carpeta input")
    exit()
# 2
if len(input.columns) != 1:
    print("El archivo ItemsGenerar.xlsx debe tener una sola columna")
    exit()
# 3    
if input.columns[0] != 'VarianteColor':
    print("El archivo ItemsGenerar.xlsx debe tener una columna llamada VarianteColor")
    exit()

# Verificando que el archivo tenga la estructura correcta
items = input["VarianteColor"]
# 4 
if items.empty:
    print("El archivo ItemsGenerar.xlsx no tiene la columna 'VarianteColor'")
    exit()
# 5
if items.dtype != 'int64':
    print("En el archivo ItemsGenerar, la columna 'VarianteColor' contiene algun valor que no es numerico")
    exit()
# 6 
for item in items:
    item = str(item)
    
    if len(item) != 10:
        print("En el archivo ItemsGenerar existe un error en: ", item)
        exit()
# 7
items = pd.unique(items)

# Mapping & ItemsGenerar -----------------------------------------------------

# 8 
if os.path.exists(Dir.carpeta_intupt + '\Mapping.csv'):
    mapping = pd.read_csv(Dir.carpeta_intupt + '\Mapping.csv')
    fecha_creacion = time.ctime(os.path.getmtime(Dir.carpeta_intupt + '\Mapping.csv'))
    print("El archivo Mapping.csv fue modificado en: ", fecha_creacion)
else:
    print("No existe el archivo Mapping.csv en la carpeta input")
    exit()

# 9
map_sku = pd.unique(mapping["sku"])
map_sku = pd.DataFrame(map_sku, columns=['sku'])
items = pd.DataFrame(items, columns=['sku'])

NoMapping = []
inner = []
for item in items['sku'].values.tolist():
    item = str(item)
    if item not in str(map_sku['sku'].values.tolist()):
        NoMapping.append(item)
        print('--- El item '+ item + ' no existe en el archivo Mapping.csv')
    else:
        inner.append(item)

if len(NoMapping) > 0:
    print('--Existen items que no estan en el archivo Mapping.csv, revise NoMapping.xlsx en carpeta output')
    NoMapping = pd.DataFrame(NoMapping, columns=['sku'], index=None)
    
    os.chdir(Dir.resultados_hoy_reportes)
    NoMapping.to_excel('NoMapping.xlsx', index=False)
    os.chdir(Dir.code)

# print("Número de items a generar:", len(inner))