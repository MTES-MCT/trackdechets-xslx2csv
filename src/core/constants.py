ETABLISSMENTS_FIELDS = [
    "siret",
    "gerepId",
    "companyTypes",
    "givenName",
    "contactEmail",
    "contactPhone",
    "contact",
    "website",
]


ROLE_FIELDS = [
    "siret",
    "email",
    "role",
]

COMPANY_TYPES = [
    "PRODUCER",
    "WASTE_CENTER",
    "TRANSPORTER",
    "COLLECTOR",
    "WASTEPROCESSOR",
    "TRADER",
    "BROKER",
    "ECO_ORGANISME",
]

ANONYMOUS_ETABLISSMENTS_FIELDS = [
    "siret",
    "name",
    "address",
    "codeNaf",
    "codeCommune",
]
MIN_ETAB_ROW = 1
MAX_ETAB_COL = 7
MIN_ROLE_ROW = 1
MAX_ROLE_COL = 3
MAX_ANON_ETAB_COL = 5

ERROR_STR = "💣 [red]Error[/red]"
VALID_STR = "[green]✔[/green]"
