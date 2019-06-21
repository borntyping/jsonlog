"""A more realistic usage example."""

import jsonlog
import logging
import click

log = logging.getLogger(__name__)


@click.group()
def main():
    jsonlog.basicConfig()


@main.command()
def action():
    logging.warning("Performing an action", {"context": [1, 2, 3]})


if __name__ == "__main__":
    main()
