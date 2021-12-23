import os


def quote(v):
    if v is None:
        v = ""
    return f'"{v}"'


def format_csv_row(lst):
    f = ";".join(lst)
    return f + ";" + os.linesep
