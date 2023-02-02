'''
This code is used to replace temporal images with professional images
'''

import os
from struct import pack
from shutil import move

def list_files(path):
    # This function lists all files in a directory and subdirectories
    files_fullname, files = [], []
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            files_fullname.append(os.path.join(root, filename))
            files.append(filename)
    return files_fullname, files

def find_item(text, n):
    # This function returns a number of first n consecutive digits in a string (item)
    consecutive, item = '', ''
    for w, word in enumerate(text):
        if word.isdigit():
            consecutive = consecutive + word
        else:
            consecutive = ''
        if len(consecutive) == n:
            item = consecutive
            break
    return item

def find_rare_characters(text):
    # This function returns a list of rare characters in a string
    permited_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.0123456789 -()'
    rare_characters = []
    for w, word in enumerate(text):
        if word not in permited_characters:
            rare_characters.append(word)
    return rare_characters

def change_characters(text, dic_changes):
    # This function changes characters in a string
    for key, value in dic_changes.items():
        text = text.replace(key, value)
    return text

def path_of_file(file_name):
    # This function returns the path of a file
    path = os.path.dirname(os.path.abspath(file_name))
    return path


path_ini = r'''C:\Users\jcarpinteyro\OneDrive - SERVICIOS SHASA S DE RL DE CV\Fotografías Subir Pagina'''

path_fin_beauty = r'''I:\BEAUTY'''
path_fin_jew = r'''I:\JEW'''
path_fin_acc = r'''I:\ACC'''
path_fin_clo = r'''I:\CLO'''
path_fin_sho = r'''I:\SHO'''

dic_path_fin = {'BEAUTY':path_fin_beauty, 'JEW':path_fin_jew, 'ACC':path_fin_acc, 'CLO':path_fin_clo, 'SHO':path_fin_sho}


'''
# list all rare characters in all images
ls_rare_chars = []
for img in ls_imgs:
    rarechar = find_rare_characters(img)
    if len(rarechar) > 0:
        ls_rare_chars = ls_rare_chars + rarechar
ls_rare_chars = list(set(ls_rare_chars))
'''

def rename_images_rarechars(path):
    dic_changes = { 'ó':'o','Ñ':'NI','&':'AND','ñ':'ni','̃':'I','̈':'','\xa0':'','́':'','Ó':'O','̂':'', 
                    '´':'','¡':'','=':'','╠':'I','á':'a','Á':'A','\uf020':'',',':'','â':'',"'":''}

    ls_imgs_fullname, ls_imgs = list_files(path)

    # replace rare characters in all images
    for i, img in enumerate(ls_imgs):
        rarechar = find_rare_characters(img)
        #print(img)
        if len(rarechar) > 0:
            previous_name = img
            new_name = change_characters(img, dic_changes)
            print('Previous name: ' + previous_name)
            print('New name:      ' + new_name)
            print('')
            newpath = path_of_file(ls_imgs_fullname[i])
            os.chdir(newpath)
            # copy file previous_name to new file with name new_name
            move(previous_name, new_name)
            

#path_ini = r'''C:\Users\fcolin\SERVICIOS SHASA S DE RL DE CV\Administrador - Fotografías Subir Pagina\2022\ACCES Y CALZADO\2022-08-19 ACCES'''

#rename_images_rarechars(path=path_ini)

