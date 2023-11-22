class Book:
    # __init__ is called when the object is created
    def __init__(self, id, title, isbn, author, year, pos_file):
        # Atributos de instancia
        self.id = id
        self.title = title
        self.isbn = isbn
        self.author = author
        self.year = year
        self.pos_file = pos_file
        self.erased = False

    def __eq__(self, o_c):
        return o_c.pos_file == self.pos_file

    def __str__(self):
        return str(self.id) + str(self.title) + str(self.isbn) + str(self.author) + str(self.year) + str(self.pos_file)

    def customer_in_pos(self, pos):
        return self.pos_file == pos

    def set_customer(self, name, isbn, author, year):
        self.title = name
        self.isbn = isbn
        self.author = author
        self.year = year

    def get_attrs_list(self):
        return [self.id, self.title, self.isbn, self.author, self.year, self.pos_file]
