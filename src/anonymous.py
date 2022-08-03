import io
from pathlib import Path

import click
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
    export_file_name = "anonymous.csv"
    wb = load_xlsx(file)
    ws_etablissements = wb.worksheets[0]

    anon_rows = AnonymousEtabRows.from_worksheet(ws_etablissements)
    anon_rows.validate()

    if not anon_rows.is_valid:
        console.print()
        console.print(
            Padding(
                ":thumbs_down: [red]This file as errors and can't be imported",
                (1, 0),
            ),
        )
        anon_rows.make_messages()
        return

    current_path = Path(".")
    console.print(":weight_lifter:[green] Exporting")
    csv_dir = current_path / "csv"
    csv_dir.mkdir(exist_ok=True)
    with open(f"csv/{export_file_name}", "w", newline="") as csvfile:
        for row in anon_rows.as_csv():
            csvfile.write(row)

    console.print(f":thumbs_up:[green] Done - Your file is ./csv/{export_file_name}")

    panel_group = Group(
        Padding(
            f"[green] scalingo --app trackdechets-production-api run --file ./csv/{export_file_name} bash",
            (1, 4),
        ),
        Padding("[yellow] then : ", (1, 0)),
        Padding(
            f"[green] node ./dist/src/scripts/bin/importAnonymousCompany.js /tmp/uploads/{export_file_name}",
            (1, 4),
        ),
    )
    console.print(
        Panel(
            panel_group,
            title="[bold green]Now you may run these commands to import csv",
        )
    )


if __name__ == "__main__":
    parse_validate_convert()
