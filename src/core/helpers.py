def process_field(value, field_name):
    if value is None:
        return value
    if field_name == "role":
        return str(value).upper().strip()
    if field_name == "contactPhone":

        cleaned = (
            str(value)
            .replace("  ", " ")
            .replace("/", " ")
            .replace("\u200b", " ")
            .strip()
        )

        if len(cleaned) and not cleaned.startswith("0"):
            cleaned = f"0{cleaned}"
        return cleaned
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
    return value.replace("\u200b", "")


def dict_read(row, fields_config):
    data = {}
    for i, cell in enumerate(row):
        field_name = fields_config[i]
        data[field_name] = clean_from_funky_chars(process_field(cell.value, field_name))
    return data
