import click

from billing.invoice import total


# The CLI entry point
@click.group()
def cli():
    """Billing tools for the finance team."""


@cli.command()
@click.argument("subtotal")
def preview(subtotal):
    """Print the invoice total for SUBTOTAL with 22% VAT and no discount."""
    # call total and print it
    click.echo(total(subtotal, "0.22", "0"))
