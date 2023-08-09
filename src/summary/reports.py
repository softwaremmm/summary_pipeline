from enum import Enum
import json
from pathlib import Path


class ReportType(Enum):
    GATEKEEPER = "gatekeeper_report.json"
    MAPPING = "competitivemapping_report.json"
    MYKROBE = "mykrobe_report.json"
    GNOMONICUS = "gnomonicus.json"


class Report:
    def __init__(self, report_type: ReportType, report_path: Path) -> None:
        self.report_type = report_type
        self.report_path = report_path
        with open(self.report_path, "r") as file:
            self.report_contents = json.load(file)


class ReportList(list):
    def retrieve(self, report_type: ReportType) -> Report:
        for report in self:
            if report.report_type == report_type:
                return report
        raise ValueError(str(report_type) + " not in collection.")

    def contains(self, report_type: ReportType) -> bool:
        found = False
        for report in self:
            if report.report_type == report_type:
                found = True

        return found

    def __str__(self) -> str:
        report_strings = []
        for report in self:
            report_strings.append(report.report_path)
        return str(report_strings)
