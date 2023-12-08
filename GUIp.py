from Book import Book, Keys
import PySimpleGUI as sG
import re
import operator

from XMLHandler import (read_books_from_xml, save_book_to_xml, delete_book_from_xml,
                        update_book_in_xml, purge_xml, set_list_to_xml)

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
filename = 'books.xml'
book_list = []
pattern_isbn = r"\d{13}"  # 13 digits (isbn-13)
pattern_year = r"\d{4}"  # four digits


def add_book(t_book_interface, book):
    """
    Add a new book to the book list, save it to the XML file, and update the table interface.

    :param t_book_interface: The representation of the book in the table.
    :param book: The book object to be added.
    """
    book_list.append(book)
    save_book_to_xml(book, filename)
    t_book_interface.append(book.get_attrs_list())


def del_book(table_data, pos_in_table):
    """
    Delete a book from the book list, the table data, and the XML file based on its position in the table.

    :param table_data: The data displayed in the book table.
    :param pos_in_table: The position of the book in the table.
    """
    book_id = table_data[pos_in_table][0]
    for b in book_list:
        if b.get_id() is book_id:
            table_data.remove(table_data[pos_in_table])
            b.erased = True
            delete_book_from_xml(b.get_id(), filename)
            break


def update_book(row_book):
    """
    Update a book in the book list and the XML file based on the provided row of book data.

    :param row_book: The row of book data to be updated.
    """
    book_id = row_book[0]
    for b in book_list:
        if b.get_id() == book_id:
            b.set_book(row_book[1], row_book[2], row_book[3], row_book[4])
            update_book_in_xml(b, filename)
            break


def sort_table(table, cols):
    """
    Sort a table by multiple columns
    :param table: a list of lists (or tuple of tuples) where each inner list
           represents a row
    :param cols: a list (or tuple) specifying the column numbers to sort by
           e.g. (1,0) would sort by column 1, then by column 0
    """
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as e:
            sG.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table


def error_dialog(msg, title='Error'):
    """
    Display an error dialog with the given message and title.

    :param msg: The error message.
    :param title: The title of the error dialog.
    """
    sG.Popup(msg, title=title, keep_on_top=True)


def format_id(id):
    """
    Format an integer ID as a string with leading zeros.

    :param id: Integer ID.
    :return: Formatted ID as a string.
    """
    return str(id).zfill(3)


def generate_id():
    """
    Generate a new ID that is not currently in use.

    :return: A new ID as a string.
    """
    if not book_list:
        return format_id(1)
    existing_ids = [book.book_info['id'] for book in book_list]  # create a list with existing IDs
    # find the first unused ID, if any
    for i in range(1, len(book_list) + 1):
        if format_id(i) not in existing_ids:
            return format_id(i)
    return format_id(len(book_list) + 1)  # if we don't find any, return length + 1


def valid_fields(*patterns, **fields):
    """
    Validate fields based on specified patterns.

    :param patterns: Regular expression patterns to validate fields.
    :param fields: Key-value pairs representing the fields to validate.
    :return: True if all fields are valid, False otherwise.
    """
    # iterate over pairs of patterns and corresponding key-value pairs from fields
    for pattern, (key, value) in zip(patterns, fields.items()):
        # if it's ISBN, remove the hyphens
        if key == 'ISBN':
            value = fields[key].replace("-", "")
        # check if the value matches the pattern
        if not re.match(pattern, str(value)):
            error_dialog(f'The {key} field is not valid.')
            return False
    return True


def sort_window():
    """
    Display a window for selecting sorting criteria.

    :return: List of selected sorting criteria.
    """
    buttons_keys = {
        'ID': Keys.ID,
        'Title': Keys.TITLE,
        'Author': Keys.AUTHOR,
        'Year': Keys.YEAR,
        'Position': Keys.POS,
    }

    layout = [
        [sG.Text('Select sorting criteria in order of priority:')],
        [sG.Button(button, key=buttons_keys[button]) for button in buttons_keys],
        [sG.Listbox([], size=(15, 5), key='SORT_PRIORITY')],
        [sG.Button('OK'), sG.Button('Cancel')]
    ]

    window = sG.Window('Sort Options', layout, keep_on_top=True, element_justification='c')

    selected_criteria = []

    while True:
        event, values = window.read()

        if event in (sG.WIN_CLOSED, 'Cancel'):
            break
        elif event == 'OK':
            if selected_criteria:
                window.close()
                return selected_criteria
        elif event in buttons_keys.values():
            if event in selected_criteria:
                selected_criteria.remove(event)
            else:
                selected_criteria.append(event)

            window['SORT_PRIORITY'].update(selected_criteria)

    window.close()


def sort_books(criteria):
    """
    Sort the book list based on the provided criteria in reverse order.
    After that, update the XML file.

    :param criteria: A list of sorting criteria for books.
    """
    for c in reversed(criteria):
        Book.key_order_criteria = c
        book_list.sort()
    set_list_to_xml(book_list, filename)


class Buttons:
    """
    Constants for the events
    """
    ADD = 'Add'
    DELETE = 'Delete'
    TABLE_DOUBLE_CLICK = f'{KEY_TABLE} Double'
    CLEAR = 'Clear'
    MODIFY = 'Modify'
    PURGE = 'Purge'
    SORT = 'Sort File'


def listen_events(window, table_data):
    while True:
        row_to_update = []
        event, values = window.read()
        if values is None:
            c_title = c_isbn = c_author = c_year = ""
        else:
            c_title = values[Keys.TITLE]
            c_isbn = values[Keys.ISBN]
            c_author = values[Keys.AUTHOR]
            c_year = values[Keys.YEAR]

        def check_valid_fields():
            # first we check if is any empty field
            if "" in (c_title, c_isbn, c_author, c_year):
                error_dialog("You can't leave any field empty.")
                return False
            return valid_fields(pattern_isbn, pattern_year, ISBN=c_isbn, Year=c_year)

        match event:
            case sG.WIN_CLOSED:
                return
            case Buttons.ADD:
                if check_valid_fields():
                    new_id = generate_id()
                    add_book(table_data, Book(new_id, c_title, c_isbn, c_author, c_year, -1))
                    window[KEY_TABLE].update(table_data)
            case Buttons.DELETE if len(values[KEY_TABLE]) > 0:
                del_book(table_data, values[KEY_TABLE][0])
                window[KEY_TABLE].update(table_data)
            case Buttons.TABLE_DOUBLE_CLICK if len(values[KEY_TABLE]) > 0:
                # when double-clicking on a record in the table, its values are set in the fields
                row = values[KEY_TABLE][0]
                window[Keys.ID].update(str(table_data[row][0]))
                window[Keys.TITLE].update(str(table_data[row][1]))
                window[Keys.ISBN].update(str(table_data[row][2]))
                window[Keys.AUTHOR].update(str(table_data[row][3]))
                window[Keys.YEAR].update(str(table_data[row][4]))
                window[Keys.POS].update(str(table_data[row][5]))
            case Buttons.CLEAR:
                window[Keys.ID].update('')
                window[Keys.TITLE].update('')
                window[Keys.ISBN].update('')
                window[Keys.AUTHOR].update('')
                window[Keys.YEAR].update('')
                window[Keys.POS].update('')
            case Buttons.MODIFY if check_valid_fields():
                for row in table_data:
                    if row[0] == values[Keys.ID]:
                        row_to_update = row
                        row[1], row[2], row[3], row[4] = c_title, c_isbn, c_author, c_year
                        break
                update_book(row_to_update)
                window[KEY_TABLE].update(table_data)
            case Buttons.PURGE:
                if purge_xml(book_list, filename):
                    table_data = [b.get_attrs_list() for b in book_list if not b.erased]
                    window[KEY_TABLE].update(table_data)
                    sG.Popup('File successfully purged.', title='Purge', keep_on_top=True)
                else:
                    sG.Popup('Nothing to purge', title='Purge', keep_on_top=True)
            case Buttons.SORT:
                selected_sort_criteria = sort_window()
                if selected_sort_criteria is not None:
                    sort_books(selected_sort_criteria)
                    sG.Popup('File sorted successfully.', title='Sorted!', keep_on_top=True)
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
    read_books_from_xml(filename, book_list)
    table_data = [b.get_attrs_list() for b in book_list if not b.erased]
    layout = [
        [sG.Table(values=table_data, headings=headings, max_col_width=50, num_rows=10,
                  display_row_numbers=False, justification='center', enable_events=True,
                  enable_click_events=True,
                  vertical_scroll_only=False, select_mode=sG.TABLE_SELECT_MODE_BROWSE,
                  expand_x=True, bind_return_key=True, key=KEY_TABLE)],
        [sG.Push(), sG.Text('Book CRUD'), sG.Push()],
        [
            sG.Column([
                [sG.Text(text), sG.Input(key=key)] for key, text in fields.items()
            ], element_justification='right', justification='center')
        ],
        [sG.Push()] +
        [sG.Button(button) for button in (Buttons.ADD, Buttons.DELETE, Buttons.MODIFY, Buttons.CLEAR)] +
        [sG.Push()],
        [sG.Button(Buttons.PURGE), sG.Push(), sG.Button(Buttons.SORT)],
        ]

    window = sG.Window('Book Management with Files', layout, finalize=True)
    window.set_min_size((1200, 0))  # sets a minimum width
    window.move_to_center()  # centering the window
    window[Keys.ID].update(disabled=True)  # we'll generate ID automatically
    window[Keys.POS].update(disabled=True)
    window[KEY_TABLE].bind("<Double-Button-1>", " Double")

    listen_events(window, table_data)  # listen until the user closes the window
    window.close()


def main():
    interface()


if __name__ == '__main__':
    main()
