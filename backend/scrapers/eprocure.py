from .base import BaseScraper
from datetime import datetime

class EProcureScraper(BaseScraper):
    def __init__(self):
        super().__init__(headless=True)
        self.base_url = "https://eprocure.gov.in/eprocure/app"

    def scrape_active_tenders(self):
        print(f"Scraping {self.base_url}")
        try:
            html = self.fetch_dynamic_content(self.base_url)
            soup = self.parse_html(html)
            
            tenders = []
            table = soup.find('table', id='activeTenders')
            if not table:
                print("Could not find activeTenders table")
                return []
                
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    title_elem = cols[0].find('a')
                    title = title_elem.text.strip() if title_elem else cols[0].text.strip()
                    # Remove the leading number e.g. "1. "
                    if ". " in title[:5]:
                        title = title.split(". ", 1)[1]
                        
                    ref_no = cols[1].text.strip()
                    closing_date_str = cols[2].text.strip()
                    
                    try:
                        # 13-Aug-2026 05:30 PM
                        dt = datetime.strptime(closing_date_str, "%d-%b-%Y %I:%M %p")
                        closing_date = dt.date()
                    except ValueError:
                        closing_date = datetime.now().date()
                        
                    tenders.append({
                        "title": title,
                        "reference_no": ref_no,
                        "agency": "eProcure/NIC",
                        "publishing_date": datetime.now().date(),
                        "closing_date": closing_date,
                        "source_url": "https://eprocure.gov.in/eprocure/app",
                        "status": "Active"
                    })
            print(f"Successfully scraped {len(tenders)} tenders.")
            return tenders
        except Exception as e:
            print(f"Error scraping eProcure: {e}")
            return []
