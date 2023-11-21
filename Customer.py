class Customer:
    headings = ['ID', 'Name', 'Bill Address', 'Phone', 'Email', 'Pos']
    fields = {
        '-ID-': 'Customer ID:',
        '-Name-': 'Customer Name:',
        '-Bill-': 'Billing Address:',
        '-Phone-': 'Phone:',
        '-Email-': 'Email:',
        '-PosFile-': 'Position into File'
    }

    # El método __init__ es llamado al crear el objeto
    def __init__(self, id, name, bill, phone, email, pos_file):
        # Atributos de instancia
        self.id = id
        self.name = name
        self.bill = bill
        self.phone = phone
        self.email = email
        self.pos_file = pos_file
        self.erased = False

    def __eq__(self, o_c):
        return o_c.pos_file == self.pos_file

    def __str__(self):
        return str(self.id) + str(self.name) + str(self.bill) + str(self.phone) + str(self.email) + str(self.pos_file)

    def customer_in_pos(self, pos):
        return self.pos_file == pos

    def set_customer(self, name, bill, phone, email):
        self.name = name
        self.bill = bill
        self.phone = phone
        self.email = email
