from Book import Book, Keys
from SerializeFile import write_to_file, update_file, read_from_file
import PySimpleGUI as sG
import re
import operator

headings = ['ID', 'Title', 'ISBN-13', 'Author', 'Year', 'Pos']
fields = {
    Keys.ID: 'Book ID:',
    Keys.TITLE: 'Title:',
    Keys.ISBN: 'ISBN-13:',
    Keys.AUTHOR: 'Author:',
    Keys.YEAR: 'Year:',
    Keys.POS: 'Position in File'
}
KEY_TABLE = 'table'
filename = 'Book.dat'
book_list = []
pattern_isbn = r"\d{13}"  # 13 digits (isbn-13)
pattern_id = r"\d{3}"  # three digits
pattern_year = r"\d{4}"  # four digits


def add_book(t_book_interface, book):
    book_list.append(book)
    write_to_file(filename, book)
    t_book_interface.append(book.get_attrs_list())


def del_book(t_book_interface, pos_in_table):
    pos_in_file = t_book_interface[pos_in_table][-1]
    c_del = None
    for o in book_list:
        if o.book_in_pos(pos_in_file):
            c_del = o
            break
    if c_del is not None:
        book_list.remove(c_del)
        t_book_interface.remove(t_book_interface[pos_in_table])
        c_del.erased = True
        update_file(filename, c_del)


def update_book(t_row_book_interface, pos_in_file):
    c_up = None
    for o in book_list:
        if o.book_in_pos(pos_in_file):
            c_up = o
            break
    if c_up is not None:
        c_up.set_book(t_row_book_interface[1], t_row_book_interface[2], t_row_book_interface[3],
                      t_row_book_interface[4])
        update_file(filename, c_up)


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
        # if it's ISBN, remove the hyphens
        if key == 'ISBN':
            value = fields[key].replace("-", "")
            print(value)
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
            c_id = values[Keys.ID]
            c_title = values[Keys.TITLE]
            c_isbn = values[Keys.ISBN]
            c_author = values[Keys.AUTHOR]
            c_year = values[Keys.YEAR]

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
                    add_book(table_data, Book(c_id, c_title, c_isbn, c_author, c_year, -1))
                    window[KEY_TABLE].update(table_data)
            case Events.DELETE if len(values[KEY_TABLE]) > 0:
                del_book(table_data, values[KEY_TABLE][0])
                window[KEY_TABLE].update(table_data)
            case Events.TABLE_DOUBLE_CLICK if len(values[KEY_TABLE]) > 0:
                # when double-clicking on a record in the table, its values are set in the fields
                row = values[KEY_TABLE][0]
                window[Keys.ID].update(disabled=True)
                window[Keys.ID].update(str(table_data[row][0]))
                window[Keys.TITLE].update(str(table_data[row][1]))
                window[Keys.ISBN].update(str(table_data[row][2]))
                window[Keys.AUTHOR].update(str(table_data[row][3]))
                window[Keys.YEAR].update(str(table_data[row][4]))
                window[Keys.POS].update(str(table_data[row][5]))
            case Events.CLEAR:
                window[Keys.ID].update(disabled=False)
                window[Keys.ID].update('')
                window[Keys.TITLE].update('')
                window[Keys.ISBN].update('')
                window[Keys.AUTHOR].update('')
                window[Keys.YEAR].update('')
                window[Keys.POS].update('')
            case Events.MODIFY if check_valid_fields():
                for t in table_data:
                    if t[-1] == int(values[Keys.POS]):
                        row_to_update = t
                        t[1], t[2], t[3], t[4] = c_title, c_isbn, c_author, c_year
                        break
                update_book(row_to_update, int(values[Keys.POS]))
                window[KEY_TABLE].update(table_data)
                window[Keys.ID].update(disabled=False)
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
    font1 = ('Consolas', 15)
    sG.theme('TealMono')
    sG.set_options(font=font1)
    read_from_file(filename, book_list)
    table_data = [b.get_attrs_list() for b in book_list if not b.erased]
    layout = [
                 [sG.Push(), sG.Text('Book CRUD'), sG.Push()]] + [
                 # each field has a width of 50
                 [sG.Text(text), sG.Push(), sG.Input(key=key, size=50)] for key, text in fields.items()] + [
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
    window[Keys.POS].update(disabled=True)
    window[KEY_TABLE].bind("<Double-Button-1>", " Double")

    listen_events(window, table_data)  # listen until the user closes the window
    window.close()


def main():
    interface()


if __name__ == '__main__':
    main()
