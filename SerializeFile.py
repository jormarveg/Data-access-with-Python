import pickle


def write_to_file(f, o_c):
    f.seek(0, 2)
    o_c.pos_file = f.tell()
    pickle.dump(o_c, f)


def update_file(f, o_c):
    f.seek(o_c.pos_file, 0)
    pickle.dump(o_c, f)


def read_from_file(f, l_c):
    f.seek(0, 0)
    while True:
        try:
            l_c.append(pickle.load(f))
        except EOFError:
            break
