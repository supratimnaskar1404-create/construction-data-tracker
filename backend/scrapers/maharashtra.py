from .nicgep import NICGEPScraper

class MaharashtraScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            base_url="https://mahatenders.gov.in/nicgep/app",
            agency_name="MahaTenders"
        )
