import argparse
from enum import Enum
import logging
from pathlib import Path
import sys

from summary.summarise import summarise


class Report(Enum):
    GATEKEEPER = "gatekeeper_report.json"
    MAPPING = "competitivemapping_report.json"
    MYKROBE = "mykrobe_report.json"
    GNOMONICUS = "gnomonicus.json"


class Arguments:
    def __init__(self, argv: list):
        parser = argparse.ArgumentParser(
            description="Process pipeline output to create a Summary JSON"
        )
        named_reports = parser.add_argument_group(title="Paths to individual reports")
        named_reports.add_argument(
            "--gatekeeper",
            dest="gatekeeper",
            help="Path to gatekeeper_report.json file",
        )
        named_reports.add_argument(
            "--mapping",
            dest="mapping",
            help="Path to competitivemapping_report.json file",
        )
        named_reports.add_argument(
            "--mykrobe", dest="mykrobe", help="Path to mykrobe_report.json file"
        )
        named_reports.add_argument(
            "--gnomonicus", dest="gnomonicus", help="Path to gnomonicus.json file"
        )
        report_list = parser.add_argument_group(title="Path to report list")
        report_list.add_argument(
            "--reports",
            nargs="+",
            dest="reports",
            help="A list of report files, the contents of which will be inferred by filename",
        )
        outputs = parser.add_argument_group(title="Output parameters")
        outputs.add_argument(
            "--output_path",
            default="Mega.json",
            dest="output",
            help="Path including name for output .json file",
        )
        args = parser.parse_args(argv)

        if args.reports:
            try:
                self.gatekeeper = self._get_report(args.reports, Report.GATEKEEPER)
            except ValueError as error:
                logging.info(error)
            try:
                self.mapping = self._get_report(args.reports, Report.MAPPING)
            except ValueError as error:
                logging.info(error)
            try:
                self.mykrobe = self._get_report(args.reports, Report.MYKROBE)
            except ValueError as error:
                logging.info(error)
            try:
                self.gnomonicus = self._get_report(args.reports, Report.GNOMONICUS)
            except ValueError as error:
                logging.info(error)
        else:
            self.gatekeeper = args.gatekeeper
            self.mapping = args.mapping
            self.mykrobe = args.mykrobe
            self.gnomonicus = args.gnomonicus
        self.output = args.output

    def _get_report(self, reports_list: list, report_type: Report) -> Path:
        for report in reports_list:
            if Path(report).name == report_type.value:
                return Path(report)
        raise ValueError(str(report_type) + " not found.")


def main():
    """CLI entry point."""
    logging.basicConfig(
        format="%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=logging.DEBUG,
    )

    cli_args = Arguments(sys.argv[1:])

    summarise(cli_args)
