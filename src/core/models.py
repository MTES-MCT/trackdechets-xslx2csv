import re

import attr
from email_validator import EmailNotValidError, validate_email
from rich.console import Console
from rich.table import Table

from .communes import CODE_COMUNES
from .constants import (
    ANONYMOUS_ETABLISSMENTS_FIELDS,
    COLLECTOR_TYPES,
    COMPANY_TYPES,
    ERROR_STR,
    ETABLISSMENTS_FIELDS,
    MAX_ANON_ETAB_COL,
    MAX_ETAB_COL,
    MAX_ROLE_COL,
    MIN_ETAB_ROW,
    MIN_ROLE_ROW,
    ROLE_FIELDS,
    VALID_STR,
    WASTE_PROCESSOR_TYPES,
    WASTE_VEHICLE_TYPES,
)
from .helpers import dict_read, format_csv_row, quote
from .naf import NAF_CODES

phone_re = re.compile(r"^(0[1-9])(?:[ _.-]?(\d{2})){4}$")

console = Console()

ERROR_FIELD = "field"
ERROR_SIRET_MISSING_FROM_ETAB = "siret_missing_from_etab"
ERROR_SIRET_HAS_NO_ADMIN = "siret_has_no_admin"
ERROR_DUPLICATE_ROLE = "duplicate_role"
ERROR_TYPES = [
    ERROR_FIELD,
    ERROR_SIRET_MISSING_FROM_ETAB,
    ERROR_SIRET_HAS_NO_ADMIN,
    ERROR_DUPLICATE_ROLE,
]


class BaseRow:
    @property
    def is_valid(self):
        if not self.validated:
            raise Exception("Not validated yet")
        return not self.errors

    def siret_is_valid(self):
        return len(str(self.siret)) == 14

    @classmethod
    def from_dict(cls, idx, the_dict):
        if all([not v for v in the_dict.values()]):  # skip empty rows
            return

        return cls(**the_dict, index=idx)


class BaseRows:
    def __iter__(self):
        yield from self.rows

    def append(self, row):
        if not self.header:
            self.header = row
        else:
            self.rows.append(row)

    def make_messages(self):
        for row in self.rows:
            for e in row.errors:
                console.print(e.as_message())
        for e in getattr(self, "errors", []):
            console.print(e.as_message())


@attr.s()
class NoAdminError:
    siret = attr.ib()

    def as_message(self):
        return f"Le siret {self.siret} de l'onglet etablissements n'a pas d'ADMIN identifié dans l'onglet roles"


@attr.s()
class RowError:
    row_number = attr.ib()
    field_name = attr.ib()
    field_value = attr.ib()
    error_type = attr.ib(default=ERROR_FIELD)

    tab = attr.ib(default="")

    @error_type.validator
    def _check_error_type(self, attribute, value):
        return value in ERROR_TYPES

    def as_str(self):
        return f"{self.field_name.capitalize()} error on row n°{self.row_number} value={self.field_value}"

    def message_error_field(self):
        return f"{self.tab.capitalize()} Ligne {self.row_number} Colonne {self.field_name}: {self.field_value} est incorrect"

    def message_error_missing_siret(self):
        return f"Roles Ligne {self.row_number} Colonne siret: {self.field_value} est absent de l'onglet etablissements"

    def message_error_siret_has_no_admin(self):
        return f"{self.tab.capitalize()} Ligne {self.row_number} Le siret {self.field_value} n'a pas d'ADMIN identifié dans l'onglet roles"

    def message_error_duplicate_role(self):
        return f"{self.tab.capitalize()} Ligne {self.row_number} Le rôle est dupliqué, un email ne peut être associé à un siret qu'un seule fois"

    def as_message(self):
        if self.error_type == ERROR_SIRET_MISSING_FROM_ETAB:
            return self.message_error_missing_siret()
        if self.error_type == ERROR_SIRET_HAS_NO_ADMIN:
            return self.message_error_siret_has_no_admin()
        if self.error_type == ERROR_DUPLICATE_ROLE:
            return self.message_error_duplicate_role()
        return self.message_error_field()


@attr.s()
class AnonymousEtabRow(BaseRow):
    index = attr.ib()
    siret = attr.ib(default="")
    name = attr.ib(default="")
    address = attr.ib(default="")
    codeNaf = attr.ib(default="")
    codeCommune = attr.ib(default="")

    errors = attr.ib(default=attr.Factory(list))
    validated = attr.ib(default=False)
    tab_name = "Établissements"

    def as_str(self):
        return f"{self.siret} {self.name} {self.siret}"

    def name_is_valid(self):

        return len(self.name) > 3

    def address_is_valid(self):

        return len(self.address) > 10

    def naf_code_is_valid(self):

        return self.codeNaf in NAF_CODES

    def code_commune_is_valid(self):

        return self.codeCommune in CODE_COMUNES

    def validate(self):
        if not self.siret_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="siret",
                    field_value=self.siret,
                    tab=self.tab_name,
                )
            )
        if not self.name_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="name",
                    field_value=self.name,
                    tab=self.tab_name,
                )
            )
        if not self.address_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="address",
                    field_value=self.address,
                    tab=self.tab_name,
                )
            )
        if not self.naf_code_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="code naf",
                    field_value=self.codeNaf,
                    tab=self.tab_name,
                )
            )
        if not self.code_commune_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="code commune",
                    field_value=self.codeCommune,
                    tab=self.tab_name,
                )
            )
        self.validated = True

    def as_csv(self):
        quoted = [
            quote(self.siret),
            quote(self.name),
            quote(self.address),
            quote(self.codeNaf),
            quote(self.codeCommune),
        ]
        return format_csv_row(quoted)


@attr.s()
class AnonymousEtabRows(BaseRows):
    header = attr.ib(default="")
    rows = attr.ib(default=attr.Factory(list))
    is_valid = attr.ib(default=False)

    def append(self, row):
        if not self.header:
            self.header = row
        else:
            self.rows.append(row)

    def validate(self):
        self.is_valid = True
        for row in self:
            row.validate()
            if not row.is_valid:
                self.is_valid = False

    def as_csv(self):
        ret = []
        ret.append(format_csv_row([quote(fn) for fn in ANONYMOUS_ETABLISSMENTS_FIELDS]))
        for row in self:
            ret.append(row.as_csv())
        return ret

    def make_messages(self):
        for row in self.rows:
            for e in row.errors:
                console.print(e.as_message())
        for e in getattr(self, "errors", []):
            console.print(e.as_message())

    @classmethod
    def from_worksheet(cls, worksheet):
        etab_rows = []
        idx = 1
        for row in worksheet.iter_rows(min_row=MIN_ETAB_ROW, max_col=MAX_ANON_ETAB_COL):
            data = dict_read(row, ANONYMOUS_ETABLISSMENTS_FIELDS)
            if idx != 1:
                etab_row = AnonymousEtabRow.from_dict(idx, data)

                if etab_row:
                    etab_rows.append(etab_row)
            idx += 1

        return cls(rows=etab_rows)


@attr.s()
class EtabRow(BaseRow):
    index = attr.ib()
    siret = attr.ib(default="")
    gerepId = attr.ib(default="")
    companyTypes = attr.ib(default=attr.Factory(list))
    collectorTypes = attr.ib(default=attr.Factory(list))
    wasteProcessorTypes = attr.ib(default=attr.Factory(list))
    wasteVehiclesTypes = attr.ib(default=attr.Factory(list))
    givenName = attr.ib(default="")
    contactEmail = attr.ib(default="")
    contactPhone = attr.ib(default="")
    contact = attr.ib(default="")
    website = attr.ib(default="")

    errors = attr.ib(default=attr.Factory(list))
    validated = attr.ib(default=False)
    tab_name = "Établissements"

    def as_str(self):
        return f"{self.siret} {self.givenName} {self.contactEmail}"

    def as_list(self):
        return [
            str(self.index),
            self.siret,
            self.gerepId,
            ",".join(self.companyTypes),
            ",".join(self.collectorTypes or []),
            ",".join(self.wasteProcessorTypes or []),
            ",".join(self.wasteVehiclesTypes or []),
            self.givenName,
            self.contactEmail,
            self.contactPhone,
            self.contact,
            self.website,
            ERROR_STR if not self.is_valid else VALID_STR,
        ]

    def as_csv(self):

        quoted = [
            quote(self.siret),
            quote(self.gerepId),
            ",".join(self.companyTypes),
            ",".join(self.collectorTypes or []),
            ",".join(self.wasteProcessorTypes or []),
            ",".join(self.wasteVehiclesTypes or []),
            quote(self.givenName),
            quote(self.contactEmail),
            quote(self.contactPhone),
            quote(self.contact),
            quote(self.website),
        ]
        return format_csv_row(quoted)

    def company_types_are_valid(self):
        if not self.companyTypes:
            return False
        return all([c_type in COMPANY_TYPES for c_type in self.companyTypes])

    def collector_types_are_valid(self):
        if not self.collectorTypes:
            return True
        if "COLLECTOR" not in self.companyTypes:
            return False
        return all([c_type in COLLECTOR_TYPES for c_type in self.collectorTypes])

    def waste_processor_types_are_valid(self):
        if not self.wasteProcessorTypes:
            return True
        if "WASTEPROCESSOR" not in self.companyTypes:
            return False

        return all(
            [c_type in WASTE_PROCESSOR_TYPES for c_type in self.wasteProcessorTypes]
        )

    def waste_vehicle_types_are_valid(self):
        if not self.wasteVehiclesTypes:
            return True
        if "WASTE_VEHICLES" not in self.companyTypes:
            return False
        return all(
            [c_type in WASTE_VEHICLE_TYPES for c_type in self.wasteVehiclesTypes]
        )

    def phone_number_is_valid(self):
        if not self.contactPhone:
            return True
        return phone_re.match(self.contactPhone) is not None

    def email_is_valid(self):
        if not self.contactEmail:
            return True
        try:
            validate_email(
                self.contactEmail,
                allow_smtputf8=False,
                check_deliverability=False,
                dns_resolver=None,
            )
            return True
        except EmailNotValidError:
            return False

    def validate(self):

        if not self.siret_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="siret",
                    field_value=self.siret,
                    tab=self.tab_name,
                )
            )
        if not self.company_types_are_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="companyTypes",
                    field_value=self.companyTypes,
                    tab=self.tab_name,
                )
            )
        if not self.collector_types_are_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="collectorTypes",
                    field_value=self.collectorTypes,
                    tab=self.tab_name,
                )
            )
        if not self.waste_processor_types_are_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="wasteProcessorTypes",
                    field_value=self.wasteProcessorTypes,
                    tab=self.tab_name,
                )
            )
        if not self.waste_vehicle_types_are_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="wasteVehiclesTypes",
                    field_value=self.wasteVehiclesTypes,
                    tab=self.tab_name,
                )
            )
        if not self.phone_number_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="contactPhone",
                    field_value=self.contactPhone,
                    tab=self.tab_name,
                )
            )
        if not self.email_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="contactEmail",
                    field_value=self.contactEmail,
                    tab=self.tab_name,
                )
            )
        self.validated = True

    def validate_has_admin(self, admin_sirets):
        if self.siret not in admin_sirets:
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="siret",
                    field_value=self.siret,
                    tab=self.tab_name,
                    error_type=ERROR_SIRET_HAS_NO_ADMIN,
                )
            )
            self.validated = True


@attr.s()
class EtabRows(BaseRows):
    header = attr.ib(default="")
    rows = attr.ib(default=attr.Factory(list))
    is_valid = attr.ib(default=False)

    def append(self, row):
        if not self.header:
            self.header = row
        else:
            self.rows.append(row)

    def sirets(self):
        return list(set([row.siret for row in self if row.siret and row.is_valid]))

    def validate(self):
        self.is_valid = True
        for row in self:
            row.validate()
            if not row.is_valid:
                self.is_valid = False

    def validate_have_admin(self, admin_sirets):
        for row in self:
            row.validate_has_admin(admin_sirets)
            if not row.is_valid:
                self.is_valid = False

    def as_csv(self):
        ret = []
        ret.append(format_csv_row([quote(fn) for fn in ETABLISSMENTS_FIELDS]))
        for row in self:
            ret.append(row.as_csv())
        return ret

    def as_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("N°")
        for field in ETABLISSMENTS_FIELDS:
            table.add_column(field)
        for row in self:
            table.add_row(*row.as_list())
        console.print(table)

    @classmethod
    def from_worksheet(cls, worksheet):
        etab_rows = []
        idx = 1
        for row in worksheet.iter_rows(min_row=MIN_ETAB_ROW, max_col=MAX_ETAB_COL):
            data = dict_read(row, ETABLISSMENTS_FIELDS)

            if idx != 1:
                etab_row = EtabRow.from_dict(idx, data)

                if etab_row:
                    etab_rows.append(etab_row)
            idx += 1
        return cls(rows=etab_rows)


@attr.s()
class RoleRow(BaseRow):
    index = attr.ib()
    siret = attr.ib()
    email = attr.ib()
    role = attr.ib()
    errors = attr.ib(default=attr.Factory(list))
    validated = attr.ib(default=False)
    tab_name = "Rôles"

    def as_str(self):
        return f"{self.siret} {self.role} {self.email}"

    def as_list(self):
        return [
            str(self.index),
            self.siret,
            self.email,
            self.role,
            ERROR_STR if not self.is_valid else VALID_STR,
        ]

    def as_csv(self):

        quoted = [
            quote(self.siret),
            quote(self.email),
            quote(self.role),
        ]
        return format_csv_row(quoted)

    def role_is_valid(self):
        return self.role in ["MEMBER", "ADMIN"]

    def siret_belongs_to(self, etab_sirets):
        return self.siret in etab_sirets

    def email_is_valid(self):
        if not self.email:
            return False

        try:
            validate_email(
                self.email,
                allow_smtputf8=False,
                check_deliverability=False,
                dns_resolver=None,
            )
            return True
        except EmailNotValidError:
            return False

    def validate(self, etab_sirets):
        if not self.role_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="role",
                    field_value=self.role,
                    tab=self.tab_name,
                )
            )
        if not self.siret_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="siret",
                    field_value=self.siret,
                    tab=self.tab_name,
                )
            )
        if not self.siret_belongs_to(etab_sirets):
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="siret",
                    field_value=self.siret,
                    tab="roles",
                    error_type=ERROR_SIRET_MISSING_FROM_ETAB,
                )
            )
        if not self.email_is_valid():
            self.errors.append(
                RowError(
                    row_number=self.index,
                    field_name="email",
                    field_value=self.email,
                    tab=self.tab_name,
                )
            )
        self.validated = True

    def mark_as_duplicate(self):
        self.errors.append(
            RowError(
                row_number=self.index,
                field_name="email",
                field_value=self.email,
                tab=self.tab_name,
                error_type=ERROR_DUPLICATE_ROLE,
            )
        )


@attr.s()
class RoleRows(BaseRows):
    header = attr.ib(default="")
    rows = attr.ib(default=attr.Factory(list))
    is_valid = attr.ib(default=False)
    errors = attr.ib(default=attr.Factory(list))

    def admin_sirets(self):
        return list(
            set([row.siret for row in self if row.siret and row.role == "ADMIN"])
        )

    def as_csv(self):
        ret = []
        ret.append(format_csv_row([quote(fn) for fn in ROLE_FIELDS]))
        for row in self:
            ret.append(row.as_csv())
        return ret

    def validate(self, etab_sirets):

        self.is_valid = True
        for row in self:
            row.validate(etab_sirets)
            if not row.is_valid:
                self.is_valid = False

        # Check for duplicates
        pairs = [f"{row.siret}_{row.email}" for row in self]
        seen = set()
        duplicates_idx = []
        for idx, pair in enumerate(pairs):

            if pair in seen:
                duplicates_idx.append(idx)
                self.rows[idx].mark_as_duplicate()

            if pair not in seen:
                seen.add(pair)

        if duplicates_idx:
            self.is_valid = False

    def as_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("N°")
        for field in ROLE_FIELDS:
            table.add_column(field)
        for row in self:
            table.add_row(*row.as_list())
        console.print(table)

    @classmethod
    def from_worksheet(cls, worksheet):
        role_rows = []
        idx = 1
        for row in worksheet.iter_rows(min_row=MIN_ROLE_ROW, max_col=MAX_ROLE_COL):
            data = dict_read(row, ROLE_FIELDS)
            if idx != 1:
                role_row = RoleRow.from_dict(idx, data)

                if role_row:
                    role_rows.append(role_row)
            idx += 1
        return cls(rows=role_rows)
