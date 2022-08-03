import io
from pathlib import Path

import click
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from openpyxl import load_workbook
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel

from core.models import AnonymousEtabRows

console = Console()


def load_xlsx(file):
    wb = load_workbook(filename=file)

    return wb


help_txt = ""
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class RichHelp(click.Command):
    """Custom help formatter"""

    def format_help(self, ctx, formatter):
        sio = io.StringIO()
        h_console = Console(file=sio, force_terminal=True)
        h_console.print(help_txt)
        formatter.write(sio.getvalue())


@click.command(cls=RichHelp, context_settings=CONTEXT_SETTINGS)
@click.argument("file", default="file.xlsx")
def parse_validate_convert(file):
    wb = load_xlsx(file)
    ws_etablissements = wb.worksheets[0]

    etab_rows = AnonymousEtabRows.from_worksheet(ws_etablissements)
    etab_rows.validate()

    if not etab_rows.is_valid:
        etab_rows.make_messages()
        print("error")
        return

    with open("anonymous.csv", "w", newline="") as csvfile:
        for row in etab_rows.as_csv():
            csvfile.write(row)


if __name__ == "__main__":
    parse_validate_convert()
