class Keys:
    ID = 'id'
    TITLE = 'title'
    ISBN = 'isbn'
    AUTHOR = 'author'
    YEAR = 'year'
    POS = 'pos_file'


class Book:
    # The __init__ method is called when the object is created.
    def __init__(self, id, title, isbn, author, year, pos_file):
        # Instance attributes stored in a dictionary
        self.book_info = {
            Keys.ID: id,
            Keys.TITLE: title,
            Keys.ISBN: isbn,
            Keys.AUTHOR: author,
            Keys.YEAR: year,
            Keys.POS: pos_file,
        }
        self.erased = False

    # The __eq__ method defines equality based on the 'pos_file' attribute.
    def __eq__(self, other_book):
        return other_book.book_info[Keys.POS] == self.book_info[Keys.POS]

    # The __str__ method returns a string representation of the object.
    def __str__(self):
        return str(self.book_info)

    # The book_in_pos method checks if the book is in a specific position.
    def book_in_pos(self, pos):
        return self.book_info[Keys.POS] == pos

    # The set_book method updates the book's information.
    def set_book(self, title, isbn, author, year):
        self.book_info.update({
            Keys.TITLE: title,
            Keys.ISBN: isbn,
            Keys.AUTHOR: author,
            Keys.YEAR: year
        })

    def get_pos(self):
        return self.book_info[Keys.POS]

    def set_pos(self, pos):
        self.book_info[Keys.POS] = pos

    def get_attrs_list(self):
        """
        # The get_attrs_dict method returns the list containing all attributes.
        """
        return list(self.book_info.values())
