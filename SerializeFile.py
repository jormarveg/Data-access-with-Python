import pickle


def write_to_file(filename, obj):
    """
    Write the given object to the specified file.

    :param filename: The name of the file to write to.
    :param obj: The object to be written.
    """
    with open(filename, 'ab') as f:
        f.seek(0, 2)
        obj.set_pos(f.tell())
        pickle.dump(obj, f)


def update_file(filename, obj):
    """
    Update the specified file with the given object.

    :param filename: The name of the file to update.
    :param obj: The object to be updated.
    """
    with open(filename, 'rb+') as f:
        f.seek(obj.get_pos(), 0)
        pickle.dump(obj, f)


def read_from_file(filename, obj_list):
    """
    Read objects from the specified file and append them to the given list.
    If the file doesn't exist, create an empty file.

    :param filename: The name of the file to update.
    :param obj_list: The list to which the objects will be appended
    """
    try:
        with open(filename, 'rb') as f:
            f.seek(0, 0)
            while True:
                try:
                    obj_list.append(pickle.load(f))
                except EOFError:
                    break
    except FileNotFoundError:
        create_file(filename)


def create_file(filename):
    """
    Create an empty file with the specified filename.
    :param filename: The name of the file
    """
    open(filename, 'wb').close()  # create an empty file
