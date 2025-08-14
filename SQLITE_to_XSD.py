from pathlib import Path

from otlmow_gui.Domain.logger.OTLLogger import OTLLogger
from otlmow_gui.Domain.util.XSDCreator import XSDCreator

if __name__ == "__main__":
    OTLLogger.init()
    input_path = Path("C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\wegkant_extensive_testing\\wegkant-3.db")
    output_path = Path("C:\\Users\\chris\\Documents\\job_related\\wegen_en_verkeer\\new_python_otl_wizard\\testData\\wegkant_extensive_testing\\wegkant-3.xsd")

    XSDCreator.create_xsd_from_subset(subset_path=input_path,xsd_path=output_path)