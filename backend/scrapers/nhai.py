from .nicgep import NICGEPScraper

class NHAIScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            base_url="https://etenders.gov.in/eprocure/app",
            agency_name="NHAI"
        )
