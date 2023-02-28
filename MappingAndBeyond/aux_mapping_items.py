# List all files in a directory and subdirectories as well as the creation date of each file.
import os
import datetime
import pandas as pd

def ptitle(string):
    '''This function prints a title.'''
    print('\n'+'-'*50+'\n'+string+'\n'+'-'*50+'\n')

def loading(i, n):
    '''This function prints the loading bar.'''
    p = round(i/n*100, 2)
    to_print = '\r  Progreso: [' + '|'*int(p) + '-'*(100-int(p)) + ']' + str(int(p)) + '%'
    if p == int(p):
        print(to_print)

def extract_sku(string, largo=10):
    # sku is a string of 10 digits togheter in a string
    sku, sku_10 = "", "0"
    i_ant = 0
    for i in range(len(string)):
        if string[i].isdigit():
            if i_ant == i-1:
                sku += string[i]
            else:
                sku = string[i]
            i_ant = i
            if len(sku) == largo:
                sku_10 = sku
    return sku_10

def find_bu_in_string(string, bu):
    '''This function finds bu in a string.'''
    capital_string = string.upper()
    bu = bu.upper()
    if bu in capital_string:
        return 1
    else:
        return 0

def find_unique_bu(row):
    '''This function asignes the name of the BU if rca is 1.'''
    if row['rca'] == 1 and row['ropa'] == 1:
        return 'ROPA'
    elif row['rca'] == 1 and row['calzado'] == 1:
        return 'CALZADO'
    elif row['rca'] == 1 and row['accesorios'] == 1:
        return 'ACCESORIOS'
    else:
        return 'NA'


def extract_suffix_method_1(string):
    '''
    This function extracts the suffix of a string.
    suffix is defined as the first digit after the last '_' in the string.
    '''
    suffix = '0'
    try:
        position_last_underscore = string.rfind('_')
        value = string[position_last_underscore+1:position_last_underscore+2]
        if value.isdigit():
            suffix = value
    except:
        suffix = '0'
    return suffix

def extract_suffix_method_2(string):
    '''
    This function extracts the suffix of a string.
    suffix is defined as the first digit before the last '.' in the string just if the 2nd character before the last '.' is not a digit
    '''
    suffix = '0'
    try:
        position_last_dot = string.rfind('.')
        first_value_before_last_dot = string[position_last_dot-1:position_last_dot]
        second_value_before_last_dot = string[position_last_dot-2:position_last_dot-1]
        if first_value_before_last_dot.isdigit() and not second_value_before_last_dot.isdigit():
            suffix = first_value_before_last_dot
    except:
        suffix = '0'
    return suffix

def extract_suffix(string):
    suffix_method_1 = extract_suffix_method_1(string)
    suffix_method_2 = extract_suffix_method_2(string)
    if suffix_method_1 == '0':
        return suffix_method_2
    else:
        return suffix_method_1

def extract_version(string):
    '''
    This function extracts the version of a string.
    version is defined as the digit between the last '(' and the last ')' in the string.
    '''
    version = '0'
    try:
        position_last_left_parenthesis = string.rfind('(')
        position_last_right_parenthesis = string.rfind(')')
        value = string[position_last_left_parenthesis+1:position_last_right_parenthesis]
        if value.isdigit():
            version = value
    except:
        version = '0'
    return version

def extract_type_file(string):
    '''
    This function extracts the type of file of a string.
    type_file is defined as the string after the last '.' in the string.
    '''
    type_file = ''
    try:
        position_last_dot = string.rfind('.')
        type_file = string[position_last_dot+1:]
    except:
        type_file = ''
    return type_file


def separate_filename_path(string):
    '''
    This function separates the filename and the path of a string.
    '''
    position_last_slash = string.rfind('\\')
    filename = string[position_last_slash+1:]
    path = string[:position_last_slash]
    return filename, path 

def count_files(mainpath):
    '''This function counts the number of files in a directory and subdirectories.'''
    count = 0
    for root, dirs, files in os.walk(mainpath):
        count += len(files)
    return count

def list_files_in_directory(mainpath):
    '''This function lists all files in a directory and subdirectories.'''
    files = []
    for root, dirs, files in os.walk(mainpath):
        for file in files:
            files.append(os.path.join(root, file))
    return files

def list_items_in_directory(mainpath):
    '''This function lists all items in a directory and subdirectories.'''
    items = []
    for root, dirs, files in os.walk(mainpath):
        for file in files:
            item = extract_sku(file)
            if item != '0' and item not in items:
                items.append(item)
    return items

def map_files(mainpath, saveas):
    '''
    This function maps the files in a directory and subdirectories and 
    returns a dictionary with the files, the creation date, the sku and the suffix.
    '''
    ptitle('  Mapeando archivos de fotos')
    nfiles = count_files(mainpath)
    ls_filefullnames, ls_filenames, ls_paths, ls_creation_dates, ls_skus, ls_suffixes, ls_versions = [], [], [], [], [], [], []
    ls_type = []
    f = 0
    for root, dirs, files in os.walk(mainpath):
        
        for file in files:
            f += 1
            loading(f, nfiles)
            ls_filefullnames.append(os.path.join(root, file))
            filename, path = separate_filename_path(os.path.join(root, file))
            ls_filenames.append(filename)
            ls_paths.append(path)
            ls_creation_dates.append(os.path.getmtime(os.path.join(root, file)))
            ls_skus.append(extract_sku(file))
            ls_suffixes.append(extract_suffix(file))
            ls_versions.append(extract_version(file))
            ls_type.append(extract_type_file(file))
    ls_paths = [path[len(mainpath):] for path in ls_paths]
    ls_creation_dates = [datetime.datetime.fromtimestamp(x) for x in ls_creation_dates]

    ptitle('  Mapeando archivos de fotos')
    print(' - Items escaneados correctamente')
    print(' - Guardando archivo de mapeo de items...')
    dic_files = {'filefullname':ls_filefullnames, 'filename':ls_filenames, 'path':ls_paths, 'creation_date':ls_creation_dates, 'sku':ls_skus, 'suffix':ls_suffixes, 'version':ls_versions, 'type':ls_type}
    df_files = pd.DataFrame(dic_files)
    df_files['key'] = df_files['sku'] + '_' + df_files['suffix']
    df_files['ropa'] = df_files['path'].apply(lambda x: find_bu_in_string(x, 'ropa'))
    df_files['calzado'] = df_files['path'].apply(lambda x: find_bu_in_string(x, 'calz'))
    df_files['accesorios'] = df_files['path'].apply(lambda x: find_bu_in_string(x, 'acces'))
    df_files['rca'] = df_files.apply(lambda x: x['ropa'] + x['calzado'] + x['accesorios'], axis=1)
    df_files['BU'] = df_files.apply(lambda x: find_unique_bu(x), axis=1)


    ls_cols = ['sku', 'creation_date', 'path', 'filename', 'type','key',  'suffix', 'version']
    # Limpiando mapping
    
    #df_files = df_files[['sku', 'creation_date', 'path', 'filename', 'key',  'suffix', 'version']]
    
    df_files = df_files[ls_cols]
    # order by creation date


    df_files = df_files.sort_values(by=['creation_date'], ascending=False)
    df_files = df_files[df_files['sku'] != '0'].reset_index(drop=True)

    df_files.to_csv(saveas, index=False)
    print(' - Se han guardado los items en el archivo ' + saveas)
    ptitle('  Mapeo concluído')


    return df_files



'''  


'''

#path_fotos = open('path.txt', 'r').readline()
path_fotos = r'C:\Users\fcolin\OneDrive - SERVICIOS SHASA S DE RL DE CV\CONNECT'

#mapping = os.getcwd()
#path_out = r'''C:\Users\fcolin\Documents\GitHub\Codigo-IMPEX.V.2\out'''
#path_out = os.path.join(mapping + '\out')

#nom_items_mapping = os.path.join(r'\out', 'Mapping.csv')
nom_items_mapping2 = os.path.join('S:\OMNI\HerramientasCode\MappingDiario', 'Mapping.csv')
#df = map_files(path_fotos, saveas=nom_items_mapping)






df2 = map_files(path_fotos, saveas=nom_items_mapping2)

#print(' - Creando archivo Excel Mapping...')
#df = pd.read_csv(nom_items_mapping, dtype={'key':str, 'creation_date':str, 'path':str, 'filename':str, 'sku':str, 'suffix':str, 'version':str, 'BU':str})

#os.chdir(path_out)
#pd.DataFrame(df).to_excel("Mapping.xlsx",   index=False)
