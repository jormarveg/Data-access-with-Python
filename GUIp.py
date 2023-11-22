from Book import Book
from SerializeFile import write_to_file, update_file, read_from_file
import PySimpleGUI as sG
import re
import operator

KEY_ID = 'id'
KEY_TITLE = 'title'
KEY_ISBN = 'isbn'
KEY_AUTHOR = 'author'
KEY_YEAR = 'year'
KEY_POS = 'pos_file'
KEY_TABLE = 'table'

headings = ['ID', 'Title', 'ISBN-13', 'Author', 'Year', 'Pos']
fields = {
    KEY_ID: 'Book ID:',
    KEY_TITLE: 'Title:',
    KEY_ISBN: 'ISBN-13:',
    KEY_AUTHOR: 'Author:',
    KEY_YEAR: 'Year:',
    KEY_POS: 'Position in File'
}

filename = 'Book.dat'
book_list = []
# ISBN-13 with hyphens ("000-0-000-00000-0")
pattern_isbn = r'\d{3}-\d{1}-\d{3}-\d{5}-\d{1}'
pattern_id = r"\d{3}"  # three numbers
pattern_year = r"\d{4}"  # four numbers
try:
    book_file = open(filename, 'rb+')
except FileNotFoundError:  # if file doesn't exist
    book_file = open(filename, 'wb+')  # it creates it


def add_book(t_customer_interface, book):
    book_list.append(book)
    write_to_file(book_file, book)
    t_customer_interface.append(book.get_attrs_list())


def del_customer(t_customer_interface, pos_in_table):
    pos_in_file = t_customer_interface[pos_in_table][-1]
    cdel = None
    for o in book_list:
        if o.customer_in_pos(pos_in_file):
            cdel = o
            break
    if cdel is not None:
        book_list.remove(cdel)
        t_customer_interface.remove(t_customer_interface[pos_in_table])
        cdel.erased = True
        update_file(book_file, cdel)


def update_customer(t_row_customer_interface, pos_in_file):
    cdel = None
    for o in book_list:
        if o.customer_in_pos(pos_in_file):
            cdel = o
            break
    if cdel is not None:
        cdel.set_customer(t_row_customer_interface[1], t_row_customer_interface[2], t_row_customer_interface[3],
                          t_row_customer_interface[4])
        update_file(book_file, cdel)


def sort_table(table, cols):
    """ sort a table by multiple columns
        table: a list of lists (or tuple of tuples) where each inner list
               represents a row
        cols:  a list (or tuple) specifying the column numbers to sort by
               e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as e:
            sG.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table


def error_dialog(msg, title='Error'):
    sG.Popup(msg, title=title, keep_on_top=True)


def valid_fields(*patterns, **fields):
    # iterate over pairs of patterns and corresponding key-value pairs from fields
    for pattern, (key, value) in zip(patterns, fields.items()):
        # check if the value matches the pattern
        if not re.match(pattern, str(value)):
            error_dialog(f'The {key} field is not valid.')
            return False
    return True


class Events:
    """
    Constants for the events
    """
    ADD = 'Add'
    DELETE = 'Delete'
    TABLE_DOUBLE_CLICK = f'{KEY_TABLE} Double'
    CLEAR = 'Clear'
    MODIFY = 'Modify'


def listen_events(window, table_data):
    while True:
        row_to_update = []
        event, values = window.read()
        if values is None:
            c_id = c_title = c_isbn = c_author = c_year = ""
        else:
            c_id = values[KEY_ID]
            c_title = values[KEY_TITLE]
            c_isbn = values[KEY_ISBN]
            c_author = values[KEY_AUTHOR]
            c_year = values[KEY_YEAR]

        def check_valid_fields():
            # first we check if is any empty field
            if "" in (c_id, c_title, c_isbn, c_author, c_year):
                error_dialog("You can't leave any field empty.")
                return False
            return valid_fields(pattern_id, pattern_isbn, pattern_year, ID=c_id, ISBN=c_isbn, Year=c_year)

        match event:
            case sG.WIN_CLOSED:
                return
            case Events.ADD:
                if check_valid_fields():
                    add_book(table_data,
                             Book(c_id, c_title, c_isbn, c_author, c_year, -1))
                    window[KEY_TABLE].update(table_data)
            case Events.DELETE if len(values[KEY_TABLE]) > 0:
                del_customer(table_data, values[KEY_TABLE][0])
                window[KEY_TABLE].update(table_data)
            case Events.TABLE_DOUBLE_CLICK if len(values[KEY_TABLE]) > 0:
                # when double-clicking on a record in the table, its values are set in the fields
                row = values[KEY_TABLE][0]
                window[KEY_ID].update(disabled=True)
                window[KEY_ID].update(str(table_data[row][0]))
                window[KEY_TITLE].update(str(table_data[row][1]))
                window[KEY_ISBN].update(str(table_data[row][2]))
                window[KEY_AUTHOR].update(str(table_data[row][3]))
                window[KEY_YEAR].update(str(table_data[row][4]))
                window[KEY_POS].update(str(table_data[row][5]))
            case Events.CLEAR:
                window[KEY_ID].update(disabled=False)
                window[KEY_ID].update('')
                window[KEY_TITLE].update('')
                window[KEY_ISBN].update('')
                window[KEY_AUTHOR].update('')
                window[KEY_YEAR].update('')
                window[KEY_POS].update('')
            case Events.MODIFY if check_valid_fields():
                for t in table_data:
                    if t[-1] == int(values[KEY_POS]):
                        row_to_update = t
                        t[1], t[2], t[3], t[4] = c_title, c_isbn, c_author, c_year
                        break
                update_customer(row_to_update, int(values[KEY_POS]))
                window[KEY_TABLE].update(table_data)
                window[KEY_ID].update(disabled=False)
        if isinstance(event, tuple):
            print(event)
            print(values)
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # You can also call Table.get_last_clicked_position to get the cell clicked
            if event[0] == KEY_TABLE and event[2][0] == -1:  # Header was clicked
                col_num_clicked = event[2][1]
                table_data = sort_table(table_data, (col_num_clicked, 0))
                window[KEY_TABLE].update(table_data)


def interface():
    font1 = ('Arial', 12)
    sG.theme('TealMono')
    sG.set_options(font=font1)
    read_from_file(book_file, book_list)
    table_data = [b.get_attrs_list() for b in book_list if not b.erased]

    layout = [
                 [sG.Push(), sG.Text('Book CRUD'), sG.Push()]] + [
                 [sG.Text(text), sG.Push(), sG.Input(key=key)] for key, text in fields.items()] + [
                 [sG.Push()] +
                 [sG.Button(button) for button in (Events.ADD, Events.DELETE, Events.MODIFY, Events.CLEAR)] +
                 [sG.Push()],
                 [sG.Table(values=table_data, headings=headings, max_col_width=50, num_rows=10,
                           display_row_numbers=False, justification='center', enable_events=True,
                           enable_click_events=True,
                           vertical_scroll_only=False, select_mode=sG.TABLE_SELECT_MODE_BROWSE,
                           expand_x=True, bind_return_key=True, key=KEY_TABLE)],
                 [sG.Button('Purge'), sG.Push(), sG.Button('Sort File')],
             ]
    window = sG.Window('Book Management with Files', layout, finalize=True)
    window.set_min_size((800, 0))  # sets a minimum width
    window.move_to_center()  # centering the window
    window[KEY_POS].update(disabled=True)
    window[KEY_TABLE].bind("<Double-Button-1>", " Double")

    listen_events(window, table_data)  # listen until the user closes the window
    window.close()


interface()
book_file.close()
