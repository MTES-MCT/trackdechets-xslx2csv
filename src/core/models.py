import re

import attr
from email_validator import EmailNotValidError, validate_email
from rich.console import Console
from rich.table import Table

from .constants import (
    COMPANY_TYPES,
    ERROR_STR,
    ETABLISSMENTS_FIELDS,
    MAX_ETAB_COL,
    MAX_ROLE_COL,
    MIN_ETAB_ROW,
    MIN_ROLE_ROW,
    ROLE_FIELDS,
    VALID_STR,
)
from .helpers import dict_read, format_csv_row, quote

phone_re = re.compile(r"^(0[1-9])(?:[ _.-]?(\d{2})){4}$")

console = Console()


@attr.s()
class RowError:
    row_number = attr.ib()
    field_name = attr.ib()
    field_value = attr.ib()
    info = attr.ib(default="")
    tab = attr.ib(default="")

    def as_str(self):
        return f"{self.field_name.capitalize()} error on row n°{self.row_number} value={self.field_value}"

    def as_message(self):
        return f"{self.tab} {self.field_name.capitalize()} error on row n°{self.row_number} value={self.field_value} {self.info}"


@attr.s()
class EtabRow:
    index = attr.ib()
    siret = attr.ib(default="")
    gerepid = attr.ib(default="")
    companyTypes = attr.ib(default=attr.Factory(list))
    givenName = attr.ib(default="")
    contactEmail = attr.ib(default="")
    contactPhone = attr.ib(default="")
    webSite = attr.ib(default="")

    errors = attr.ib(default=attr.Factory(list))
    validated = attr.ib(default=False)

    @property
    def is_valid(self):
        if not self.validated:
            raise Exception("Not validated yet")
        return not self.errors

    def as_str(self):
        return f"{self.siret} {self.givenName} {self.contactEmail}"

    def as_list(self):
        return [
            str(self.index),
            self.siret,
            self.gerepid,
            ",".join(self.companyTypes),
            self.givenName,
            self.contactEmail,
            self.contactPhone,
            self.webSite,
            ERROR_STR if not self.is_valid else VALID_STR,
        ]

    def as_csv(self):

        quoted = [
            quote(self.siret),
            quote(self.gerepid),
            ",".join(self.companyTypes),
            quote(self.givenName),
            quote(self.contactEmail),
            quote(self.contactPhone),
            quote(self.webSite),
        ]
        return format_csv_row(quoted)

    def siret_is_valid(self):
        return len(str(self.siret)) == 14

    def company_types_are_valid(self):
        return all([c_type in COMPANY_TYPES for c_type in self.companyTypes])

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
            self.errors.append(RowError(self.index, "siret", self.siret, tab="etab"))
        if not self.company_types_are_valid():
            self.errors.append(
                RowError(self.index, "companyTypes", self.companyTypes, tab="etab")
            )
        if not self.phone_number_is_valid():
            self.errors.append(
                RowError(self.index, "contactPhone", self.contactPhone, tab="etab")
            )
        if not self.email_is_valid():
            self.errors.append(
                RowError(self.index, "contactEmail", self.contactEmail, tab="etab")
            )
        self.validated = True

    @classmethod
    def from_dict(cls, idx, the_dict):
        if all([not v for v in the_dict.values()]):  # skip empty rows
            return

        return cls(**the_dict, index=idx)

    def show_errors(self):
        for e in self.errors:
            console.print(e.as_str())


@attr.s()
class EtabRows:
    header = attr.ib(default="")
    rows = attr.ib(default=attr.Factory(list))
    is_valid = attr.ib(default=False)
    siret_errors = attr.ib(default=attr.Factory(list))
    verbose_errors = attr.ib(default=attr.Factory(list))

    def append(self, row):
        if not self.header:
            self.header = row
        else:
            self.rows.append(row)

    def __iter__(self):
        yield from self.rows

    def sirets(self):
        return list(set([item.siret for item in self if item.siret]))

    def validate(self):
        self.is_valid = True
        for row in self:
            row.validate()
            if not row.is_valid:
                self.is_valid = False

    def show_errors(self):
        for idx, row in enumerate(self):
            row.show_errors()

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

    def make_messages(self):
        for row in self.rows:
            for e in row.errors:
                console.print(e.as_message())

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
class RoleRow:
    index = attr.ib()
    siret = attr.ib()
    email = attr.ib()
    role = attr.ib()
    errors = attr.ib(default=attr.Factory(list))
    validated = attr.ib(default=False)

    @property
    def is_valid(self):
        if not self.validated:
            raise Exception("Not validated yet")
        return not self.errors

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

    def siret_is_valid(self):

        return len(str(self.siret)) == 14

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
            self.errors.append(RowError(self.index, "role", self.role, tab="roles"))
        if not self.siret_is_valid():
            self.errors.append(RowError(self.index, "siret", self.siret, tab="roles"))
        if not self.siret_belongs_to(etab_sirets):
            self.errors.append(
                RowError(
                    self.index,
                    "siret",
                    self.siret,
                    "absent de l'onglet roles",
                    tab="roles",
                )
            )
        if not self.email_is_valid():
            self.errors.append(RowError(self.index, "email", self.email, tab="roles"))
        self.validated = True

    @classmethod
    def from_dict(cls, idx, the_dict):
        if all([not v for v in the_dict.values()]):
            return
        return cls(**the_dict, index=idx)

    def show_errors(self):
        for e in self.errors:
            console.print(e.as_str())


@attr.s()
class RoleRows:
    header = attr.ib(default="")
    rows = attr.ib(default=attr.Factory(list))

    is_valid = attr.ib(default=False)
    verbose_errors = attr.ib(default=attr.Factory(list))

    def append(self, row):
        if not self.header:
            self.header = row
        else:
            self.rows.append(row)

    def __iter__(self):
        yield from self.rows

    def sirets(self):
        return list(set([item.siret for item in self if item.siret]))

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

    def show_errors(self):
        for idx, row in enumerate(self):
            row.show_errors()

    def as_table(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("N°")
        for field in ROLE_FIELDS:
            table.add_column(field)
        for row in self:
            table.add_row(*row.as_list())
        console.print(table)

    def make_messages__(self):
        if not self.verbose_errors:
            return
        console.print("Roles: ")
        for error in set(self.verbose_errors):
            console.print(error)

    def make_messages(self):

        for row in self.rows:
            for e in row.errors:
                console.print(e.as_message())

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
