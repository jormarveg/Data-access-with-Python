import xml.etree.ElementTree as eT

from Book import Book, Keys

ROOT_ELEMENT = 'library'
ELEMENT_NAME = 'book'


def save_book_to_xml(book, xml_file):
    """
    Save a book to an XML file.

    :param book: Dictionary containing book information.
    :param xml_file: The name of the XML file.
    """
    root = _get_xml_root(xml_file)
    pos = len(root.findall(ELEMENT_NAME)) + 1  # increase the pos
    book.set_pos(pos)
    book_element = _create_book_element(book)
    root.append(book_element)
    _save_xml_tree(root, xml_file)


def update_book_in_xml(updated_book, xml_file):
    """
    Update a book in an XML file.

    :param updated_book: Dictionary containing updated book information.
    :param xml_file: The name of the XML file.
    """
    root = _get_xml_root(xml_file)
    for book_element in root.findall(ELEMENT_NAME):
        pos = book_element.find(Keys.POS).text
        if pos == updated_book[Keys.POS]:
            _update_book_element(book_element, updated_book)
            break
    _save_xml_tree(root, xml_file)


def delete_book_from_xml(pos, xml_file):
    """
    Delete a book from an XML file.

    :param pos: Position of the book to be deleted.
    :param xml_file: The name of the XML file.
    """
    root = _get_xml_root(xml_file)
    for book_element in root.findall(ELEMENT_NAME):
        if book_element.find(Keys.POS).text == pos:
            # root.remove(book_element)
            erased_element = book_element.find('erased')
            erased_element.text = 'True'
            break
    _save_xml_tree(root, xml_file)


def read_books_from_xml(xml_file, books):
    """
    Read books from an XML file.

    :param xml_file: The name of the XML file.
    :param books: Book list
    """
    root = _get_xml_root(xml_file)
    for book_element in root.findall(ELEMENT_NAME):
        id = book_element.find(Keys.ID).text
        title = book_element.find(Keys.TITLE).text
        isbn = book_element.find(Keys.ISBN).text
        author = book_element.find(Keys.AUTHOR).text
        year = book_element.find(Keys.YEAR).text
        pos = book_element.find(Keys.POS).text
        book = Book(id, title, isbn, author, year, pos)
        book.erased = (book_element.find('erased').text == 'True')
        books.append(book)


def _get_xml_root(xml_file):
    """
    Get the root of the XML tree.

    :param xml_file: The name of the XML file.
    :return: The root of the XML tree.
    """
    try:
        tree = eT.parse(xml_file)
    except FileNotFoundError:
        root = eT.Element(ROOT_ELEMENT)
        tree = eT.ElementTree(root)
        _save_xml_tree(root, xml_file)
    return tree.getroot()


def _save_xml_tree(root, xml_file):
    """
    Save the XML tree to a file.

    :param root: The root of the XML tree.
    :param xml_file: The name of the XML file.
    """
    tree = eT.ElementTree(root)
    tree.write(xml_file)


def _create_book_element(book):
    """
    Create an XML element for a book.

    :param book: Book object.
    :return: The XML element for the book.
    """
    book_element = eT.Element(ELEMENT_NAME)
    for key, value in book.book_info.items():
        element = eT.Element(key)
        element.text = str(value)
        book_element.append(element)
    element = eT.Element('erased')
    element.text = str(book.erased)
    book_element.append(element)
    return book_element


def _update_book_element(book_element, updated_book):
    """
    Update an XML element for a book.

    :param book_element: The XML element for the book to be updated.
    :param updated_book: Book object.
    """
    for key, value in updated_book.book_info.items():
        element = book_element.find(key)
        element.text = str(value)


def purge_xml(xml_file):
    """
    Purge books with erased set to True from an XML file.

    :param xml_file: The name of the XML file.
    :return True if successful
    """
    root = _get_xml_root(xml_file)
    books_to_remove = []

    for book_element in root.findall(ELEMENT_NAME):
        erased_value = book_element.find('erased').text
        if erased_value == 'True':
            books_to_remove.append(book_element)

    if books_to_remove:
        for book_element in books_to_remove:
            root.remove(book_element)
        _save_xml_tree(root, xml_file)
        return True
    else:
        return False
