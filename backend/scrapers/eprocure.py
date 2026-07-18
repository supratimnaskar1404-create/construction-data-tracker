from .nicgep import NICGEPScraper

class EProcureScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            base_url="https://eprocure.gov.in/eprocure/app",
            agency_name="eProcure/NIC"
        )
