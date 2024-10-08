COMPANY_TYPES_FIELD = "companyTypes"
COLLECTOR_TYPES_FIELD = "collectorTypes"
WASTE_PROCESSOR_TYPES_FIELD = "wasteProcessorTypes"
WASTE_VEHICLE_TYPES_FIELD = "wasteVehiclesTypes"

ETABLISSMENTS_FIELDS = [
    "siret",
    "gerepId",
    COMPANY_TYPES_FIELD,
    COLLECTOR_TYPES_FIELD,
    WASTE_PROCESSOR_TYPES_FIELD,
    WASTE_VEHICLE_TYPES_FIELD,
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
    "COLLECTOR",
    "WASTEPROCESSOR",
    "TRANSPORTER",
    "WASTE_VEHICLES",
    "WASTE_CENTER",
    "TRADER",
    "ECO_ORGANISME",
    "BROKER",
    "WORKER",
    "INTERMEDIARY",
    "DISPOSAL_FACILITY",
    "RECOVERY_FACILITY",
]
COLLECTOR_TYPES = [
    "NON_DANGEROUS_WASTES",
    "DANGEROUS_WASTES",
    "DEEE_WASTES",
    "OTHER_NON_DANGEROUS_WASTES",
    "OTHER_DANGEROUS_WASTES",
]
WASTE_PROCESSOR_TYPES = [
    "DANGEROUS_WASTES_INCINERATION",
    "NON_DANGEROUS_WASTES_INCINERATION",
    "CREMATION",
    "DANGEROUS_WASTES_STORAGE",
    "NON_DANGEROUS_WASTES_STORAGE",
    "INERT_WASTES_STORAGE",
    "OTHER_DANGEROUS_WASTES",
    "OTHER_NON_DANGEROUS_WASTES",
]
WASTE_VEHICLE_TYPES = ["BROYEUR", "DEMOLISSEUR"]
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
