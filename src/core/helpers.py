import os
from itertools import islice


def quote(v):
    """Let's double quote all the things"""
    if v is None:
        v = ""
    return f'"{v}"'


def format_csv_row(lst):
    f = ";".join(lst)
    return f + ";" + os.linesep


def phone_formatter(phone):
    """0612345678 -> 06 12 34 56 78"""
    chunks = []
    iterator = iter(phone)
    while chunk := "".join(islice(iterator, 2)):
        chunks.append(chunk)
    return " ".join(chunks)


def process_field(value, field_name):
    """Preprocess fields to avoid manual fixes"""
    if value is None:
        return value
    if field_name == "role":
        return str(value).upper().strip()
    if field_name == "contactPhone":
        cleaned = (
            str(value)
            .replace(" ", "")
            .replace("/", "")
            .replace("\u200b", "")
            .replace(".", "")
            .replace(",", "")
            .strip()
        )

        # is 0 missing due to any excel joke?
        if len(cleaned) == 9 and not cleaned.startswith("0"):
            cleaned = f"0{cleaned}"
        return phone_formatter(cleaned)
    if field_name == "companyTypes":
        return value.replace(" ", "").upper().split(",")
    if field_name in ["email", "contactEmail"]:
        return str(value).replace(" ", "").strip().lower()
    if field_name == "siret":
        return str(value).replace(" ", "").replace(".", "").strip().lower()
    return str(value).strip()


def clean_from_funky_chars(value):
    """Yes, our customers are that funny"""
    if not isinstance(value, str):
        return value
    return value.replace("\u200b", "").replace("\xa0", "")


def dict_read(row, fields_config):
    """Co,vert row read form openpyxl to dict according to field_config file names"""
    data = {}
    for i, cell in enumerate(row):
        field_name = fields_config[i]
        data[field_name] = clean_from_funky_chars(process_field(cell.value, field_name))
    return data
