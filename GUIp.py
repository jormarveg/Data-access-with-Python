from Customer import Customer
from SerializeFile import save_customer, modify_customer, read_customer
import PySimpleGUI as sG
import re
import operator

f_customer = open('Customer.dat', 'rb+')
lCustomer = []
pattern_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
pattern_ID = r"\d{3}"
pattern_phone = r"\d{3}-\d{6}"


def add_customer(customer, t_customer_interface, o_customer):
    customer.append(o_customer)
    save_customer(f_customer, o_customer)
    t_customer_interface.append(
        [o_customer.id, o_customer.name, o_customer.bill, o_customer.phone, o_customer.email, o_customer.pos_file])


def del_customer(customer, t_customer_interface, pos_in_table):
    pos_in_file = t_customer_interface[pos_in_table][-1]
    cdel = None
    for o in customer:
        if o.customer_in_pos(pos_in_file):
            cdel = o
            break
    if cdel is not None:
        customer.remove(cdel)
        t_customer_interface.remove(t_customer_interface[pos_in_table])
        cdel.erased = True
        modify_customer(f_customer, cdel)


def update_customer(customer, t_row_customer_interface, pos_in_file):
    cdel = None
    for o in customer:
        if o.customer_in_pos(pos_in_file):
            cdel = o
            break
    if cdel is not None:
        cdel.set_customer(t_row_customer_interface[1], t_row_customer_interface[2], t_row_customer_interface[3],
                          t_row_customer_interface[4])
        modify_customer(f_customer, cdel)


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


def interface():
    font1, font2 = ('Arial', 14), ('Arial', 16)
    sG.theme('Purple')
    sG.set_options(font=font1)
    table_data = []
    row_to_update = []
    read_customer(f_customer, lCustomer)
    for o in lCustomer:
        if not o.erased:
            table_data.append([o.id, o.name, o.bill, o.phone, o.email, o.pos_file])

    layout = [
                 [sG.Push(), sG.Text('Customer CRUD'), sG.Push()]] + [
                 [sG.Text(text), sG.Push(), sG.Input(key=key)] for key, text in Customer.fields.items()] + [
                 [sG.Push()] +
                 [sG.Button(button) for button in ('Add', 'Delete', 'Modify', 'Clear')] +
                 [sG.Push()],
                 [sG.Table(values=table_data, headings=Customer.headings, max_col_width=50, num_rows=10,
                           display_row_numbers=False, justification='center', enable_events=True,
                           enable_click_events=True,
                           vertical_scroll_only=False, select_mode=sG.TABLE_SELECT_MODE_BROWSE,
                           expand_x=True, bind_return_key=True, key='-Table-')],
                 [sG.Button('Purge'), sG.Push(), sG.Button('Sort File')],
             ]
    sG.theme('DarkBlue4')
    window = sG.Window('Customer Management with Files', layout, finalize=True)
    window['-PosFile-'].update(disabled=True)
    window['-Table-'].bind("<Double-Button-1>", " Double")
    while True:
        event, values = window.read()
        if event == sG.WIN_CLOSED:
            break
        if event == 'Add':
            valida = False
            if re.match(pattern_email, values['-Email-']):
                if re.match(pattern_ID, values['-ID-']):
                    if re.match(pattern_phone, values['-Phone-']):
                        valida = True
            if valida:
                add_customer(lCustomer, table_data,
                             Customer(values['-ID-'], values['-Name-'], values['-Bill-'], values['-Phone-'],
                                      values['-Email-'], -1))
                window['-Table-'].update(table_data)
        if event == 'Delete' and len(values['-Table-']) > 0:
            del_customer(lCustomer, table_data, values['-Table-'][0])
            window['-Table-'].update(table_data)

        if event == '-Table- Double' and len(values['-Table-']) > 0:
            row = values['-Table-'][0]
            window['-ID-'].update(disabled=True)
            window['-ID-'].update(str(table_data[row][0]))
            window['-Name-'].update(str(table_data[row][1]))
            window['-Bill-'].update(str(table_data[row][2]))
            window['-Phone-'].update(str(table_data[row][3]))
            window['-Email-'].update(str(table_data[row][4]))
            window['-PosFile-'].update(str(table_data[row][5]))
        if event == 'Clear':
            window['-ID-'].update(disabled=False)
            window['-ID-'].update('')
            window['-Name-'].update('')
            window['-Bill-'].update('')
            window['-Phone-'].update('')
            window['-Email-'].update('')
            window['-PosFile-'].update('')
        if event == 'Modify':
            valida = False
            if re.match(pattern_email, values['-Email-']):
                if re.match(pattern_ID, values['-ID-']):
                    if re.match(pattern_phone, values['-Phone-']):
                        valida = True
            if valida:
                for t in table_data:
                    if t[-1] == int(values['-PosFile-']):
                        row_to_update = t
                        t[1], t[2], t[3], t[4] = values['-Name-'], values['-Bill-'], values['-Phone-'], values[
                            '-Email-']
                        break
                update_customer(lCustomer, row_to_update, int(values['-PosFile-']))
                window['-Table-'].update(table_data)
                window['-ID-'].update(disabled=False)
        if isinstance(event, tuple):
            print(event)
            print(values)
            # TABLE CLICKED Event has value in format ('-TABLE=', '+CLICKED+', (row,col))
            # You can also call Table.get_last_clicked_position to get the cell clicked
            if event[0] == '-Table-':
                if event[2][0] == -1:  # Header was clicked
                    col_num_clicked = event[2][1]
                    table_data = sort_table(table_data, (col_num_clicked, 0))
                    window['-Table-'].update(table_data)

    window.close()


interface()
f_customer.close()
