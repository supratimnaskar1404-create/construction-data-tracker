from .base import BaseScraper
from datetime import datetime

class NICGEPScraper(BaseScraper):
    def __init__(self, base_url, agency_name):
        super().__init__(headless=True)
        self.base_url = base_url
        self.agency_name = agency_name

    def scrape_active_tenders(self):
        print(f"Scraping {self.agency_name} at {self.base_url}")
        try:
            html = self.fetch_dynamic_content(self.base_url)
            soup = self.parse_html(html)
            
            tenders = []
            table = soup.find('table', id='activeTenders')
            if not table:
                print(f"Could not find activeTenders table on {self.base_url}")
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
                        "agency": self.agency_name,
                        "publishing_date": datetime.now().date(),
                        "closing_date": closing_date,
                        "source_url": self.base_url,
                        "status": "Active"
                    })
            print(f"Successfully scraped {len(tenders)} {self.agency_name} tenders.")
            if len(tenders) == 0:
                raise Exception(f"Failed to find activeTenders table. The site might be blocking cloud IPs or the page structure changed. HTML snippet: {html[:500]}")
            return tenders
        except Exception as e:
            print(f"Error scraping {self.agency_name}: {e}")
            raise e
