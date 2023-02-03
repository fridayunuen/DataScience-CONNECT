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