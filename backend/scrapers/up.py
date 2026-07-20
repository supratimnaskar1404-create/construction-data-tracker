from .nicgep import NICGEPScraper

class UPScraper(NICGEPScraper):
    def __init__(self):
        super().__init__(
            base_url="https://etender.up.nic.in/nicgep/app",
            agency_name="UPTenders"
        )
