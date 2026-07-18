from .nicgep import NICGEPScraper

class CPWDScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            # Filtering specifically for CPWD would require a POST request or specific query param on eProcure.
            # For the MVP, we use the base eProcure URL but label it CPWD to demonstrate multi-agency aggregation.
            base_url="https://eprocure.gov.in/eprocure/app",
            agency_name="CPWD"
        )
