class Keys:
    ID = 'id'
    TITLE = 'title'
    ISBN = 'isbn'
    AUTHOR = 'author'
    YEAR = 'year'
    POS = 'pos_file'


class Book:
    key_order_criteria = Keys.TITLE

    # The __init__ method is called when the object is created.
    def __init__(self, id, title, isbn, author, year, pos_file):
        """
        Initialize a Book object with the provided attributes.

        :param id: The book ID.
        :param title: The title of the book.
        :param isbn: The ISBN of the book.
        :param author: The author of the book.
        :param year: The publication year of the book.
        :param pos_file: The position of the book in the file.
        """
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

    def __eq__(self, other):
        """
        Check if two Book objects are equal based on their attributes.

        :param other: Another Book object.
        :return: True if equal, False otherwise.
        """
        return self.book_info == other.book_info

    def __str__(self):
        """
        Return a string representation of the Book object.

        :return: String representation of the Book.
        """
        return str(self.book_info)

    # The book_in_pos method checks if the book is in a specific position.
    def book_in_pos(self, pos):
        return self.book_info[Keys.POS] == pos

    def set_book(self, title, isbn, author, year):
        self.book_info.update({
            Keys.TITLE: title,
            Keys.ISBN: isbn,
            Keys.AUTHOR: author,
            Keys.YEAR: year
        })

    def get_id(self):
        return self.book_info[Keys.ID]

    def get_pos(self):
        return self.book_info[Keys.POS]

    def set_pos(self, pos):
        self.book_info[Keys.POS] = pos

    def get_attrs_list(self):
        """
        The get_attrs_dict method returns the list containing all attributes.
        """
        return list(self.book_info.values())

    def __lt__(self, other):
        """
        Define the less-than comparison for sorting books based on `key_order_criteria`.
        Compare the criteria as str.

        :param other: Another Book object.
        :return: True if self is less than other, False otherwise.
        """
        value_self = str(self.book_info.get(Book.key_order_criteria, ''))
        value_other = str(other.book_info.get(Book.key_order_criteria, ''))
        return value_self < value_other
