from .nicgep import NICGEPScraper

class TNScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            base_url="https://tntenders.gov.in/nicgep/app",
            agency_name="TNTenders"
        )
