#import instalar_requerimientos
import os
import pandas as pd
import datetime

path_out = os.getcwd()
path_out = os.path.join(path_out, 'out')


print('\n' + '-' * 80, 'LISTADO DE ITEMS', '-' * 80)

def bld(texto):
  bs, be = "\033[1m", "\033[0;0m"
  return bs + texto + be

def extract_numbers(string):
    '''this function returns a list of numbers of one or more digits contained in a string
    '''
    numbers = []
    number = ''
    char_ant_isdigit = False
    for char in string:
        if char.isdigit() and char_ant_isdigit:
            number += char
        elif char.isdigit() and not char_ant_isdigit:
            number = char
        elif not char.isdigit() and char_ant_isdigit:
            numbers.append(number)
            number = ''
        char_ant_isdigit = char.isdigit()
    return numbers

def extract_item_number(string):
    '''this function returns the item number from a string
    the item number is a number contained in the string of lenght 10 or 13'''
    item_number = '0'
    for value in extract_numbers(string):
        if len(value) in [7, 10, 13]:
            item_number = value
    return item_number


def find_item_location(item_number, path):
    '''this function returns the path of the item with the given item number
    the item number is a number contained in the string of lenght 10 or 13
    '''
    ls_locations = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if item_number in extract_item_number(file):
                ls_locations.append(os.path.join(root, file))
    return ls_locations

def list_items(path):
    '''this function returns a list of items in the given path'''
    # Scan the directory for files
    ls_items = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            #print(dirs, files)
            item = extract_item_number(filename)
            if item not in ls_items:
                ls_items.append(item)
    return ls_items

def get_creation_date(filename):
    # This function returns the creation date of a file
    t = os.path.getmtime(filename)
    # convert to datetime object
    dt = datetime.datetime.fromtimestamp(t)
    return dt

def asign_greatest_date(item_number, path):
    '''this function returns the greatest date of the item with the given item number '''
    ls_locations = find_item_location(item_number, path)
    greatest_date = datetime.datetime(1900, 1, 1)
    for location in ls_locations:
        date = get_creation_date(location)
        if date > greatest_date:
            greatest_date = date
    return greatest_date

def list_items_and_dates(path):
    '''this function returns a list of items in the given path and a list of dates of creation of each item'''
    ls_items = []
    ls_dates = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filename = os.path.join(root, file)
            item = extract_item_number(filename)
            if item not in ls_items:
                ls_items.append(item)
                ls_dates.append(get_creation_date(filename))
    return ls_items, ls_dates


def list_items_in_folder(txt_path='path.txt'):
    # Read the first line of path.txt and saves the text of this line it into path_fotos variable
    path_fotos = open(txt_path, 'r').readline()
    path_fotos = path_fotos.replace("Ã­", "í")
    print('Escaneando items de la carpeta:', path_fotos)

    # lists the items in the given path and saves it into a txt file called items.txt
    ls_items, ls_dates = list_items_and_dates(path_fotos)
    print('Se encontraron:', len(ls_items), 'items')

    # saves the items and dates in a csv file called items_dates.csv
    df = pd.DataFrame({'item': ls_items, 'date': ls_dates})
    #file_out = os.path.join(path_out + '\items_dates.csv')
    file_out = os.path.join(path_out + '\items_dates.xlsx')
    #df.to_csv(file_out, index=False)
    df.to_excel(file_out, index=False)
    print('Se guardaron los items y fechas en el archivo items_dates.csv')
    

list_items_in_folder(txt_path='path.txt')
