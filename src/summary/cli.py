import argparse
import logging
from pathlib import Path
import sys

from summary.reports import ReportType
from summary.summarise import summarise


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
                self.gatekeeper = self._get_report(args.reports, ReportType.GATEKEEPER)
            except ValueError as error:
                logging.info(error)
            try:
                self.mapping = self._get_report(args.reports, ReportType.MAPPING)
            except ValueError as error:
                logging.info(error)
            try:
                self.mykrobe = self._get_report(args.reports, ReportType.MYKROBE)
            except ValueError as error:
                logging.info(error)
            try:
                self.gnomonicus = self._get_report(args.reports, ReportType.GNOMONICUS)
            except ValueError as error:
                logging.info(error)
        else:
            self.gatekeeper = Path(args.gatekeeper)
            self.mapping = Path(args.mapping)
            self.mykrobe = Path(args.mykrobe)
            self.gnomonicus = Path(args.gnomonicus)
        self.output = Path(args.output)

    def _get_report(self, reports_list: list, report_type: ReportType) -> Path:
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
