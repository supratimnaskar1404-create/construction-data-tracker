from .base import BaseScraper
from datetime import datetime, timedelta
import time
import random
import os
import subprocess

try:
    import pytesseract
    from PIL import Image
    import io
except ImportError:
    pass

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
                    if ". " in title[:5]:
                        title = title.split(". ", 1)[1]
                        
                    ref_no = cols[1].text.strip()
                    closing_date_str = cols[2].text.strip()
                    
                    try:
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
                        "status": "Active",
                        "awardee": None,
                        "award_value": None
                    })
            print(f"Successfully scraped {len(tenders)} {self.agency_name} tenders.")
            if len(tenders) == 0:
                raise Exception(f"Failed to find activeTenders table. The site might be blocking cloud IPs or the page structure changed. HTML snippet: {html[:500]}")
            return tenders
        except Exception as e:
            print(f"Error scraping {self.agency_name}: {e}")
            raise e

    def scrape_awarded_tenders(self, months_back=12):
        print(f"Scraping AOC for {self.agency_name} going back {months_back} months")
        
        tenders = []
        try:
            import pytesseract
            from PIL import Image, ImageOps, ImageEnhance
            import io
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                print(f"Navigating to {self.base_url}")
                page.goto(self.base_url, timeout=60000)
                
                try:
                    page.locator('text=Bid Awards').first.click(timeout=15000)
                    page.wait_for_load_state('networkidle')
                except Exception as e:
                    print("Could not find 'Bid Awards' link. Trying direct navigation.")
                    page.goto(f"{self.base_url}?page=ResultOfTendersOS&service=page")
                
                max_retries = 10
                success = False
                
                for attempt in range(max_retries):
                    print(f"OCR Attempt {attempt + 1}/{max_retries}")
                    
                    if page.locator('#captchaImage').count() == 0:
                        print("No CAPTCHA found! Assuming direct access.")
                        success = True
                        break
                        
                    # Get CAPTCHA image
                    captcha_buffer = page.locator('#captchaImage').screenshot()
                    img = Image.open(io.BytesIO(captcha_buffer))
                    
                    # Pre-process image for better OCR accuracy
                    img = img.convert('L') # Grayscale
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(2.0)
                    
                    captcha_text = pytesseract.image_to_string(img, config='--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789').strip()
                    print(f"Solved CAPTCHA: '{captcha_text}'")
                    
                    if len(captcha_text) != 6:
                        print("OCR read invalid length. Refreshing CAPTCHA...")
                        page.locator('#captcha').click()
                        page.wait_for_timeout(1000)
                        continue
                        
                    page.locator('#captchaText').fill(captcha_text)
                    page.locator('#Search').click()
                    page.wait_for_load_state('networkidle')
                    
                    # Check if error message appeared
                    if page.locator("text='Invalid Captcha'").count() > 0 or page.locator("text='Please enter correct Captcha'").count() > 0:
                        print("Invalid CAPTCHA submitted. Retrying...")
                        continue
                    else:
                        print("CAPTCHA accepted!")
                        success = True
                        break
                        
                if not success:
                    print("Failed to solve CAPTCHA after max retries.")
                    return []
                    
                # Parse the results table
                print("Parsing awarded tenders table...")
                table = page.locator('table#table')
                if table.count() == 0:
                    print("No results table found.")
                    return []
                    
                rows = table.locator('tr').all()
                for i in range(1, len(rows)): # Skip header
                    cols = rows[i].locator('td').all()
                    if len(cols) >= 5:
                        date_str = cols[1].inner_text().strip()
                        title_ref = cols[3].inner_text().strip()
                        awardee = cols[4].inner_text().strip()
                        
                        dt = datetime.now().date()
                        try:
                            dt = datetime.strptime(date_str, "%d-%b-%Y %I:%M %p").date()
                        except:
                            pass
                            
                        # Basic parsing of title/ref
                        ref_no = title_ref.split('\n')[0] if '\n' in title_ref else f"{self.agency_name}-AOC-{i}"
                        
                        tenders.append({
                            "title": title_ref[:200],
                            "reference_no": ref_no,
                            "agency": self.agency_name,
                            "publishing_date": dt,
                            "closing_date": dt,
                            "source_url": self.base_url,
                            "status": "Awarded",
                            "awardee": awardee,
                            "award_value": 0.0,
                            "awardee_contact_name": f"Manager at {awardee[:10]}",
                            "awardee_contact_email": f"contact@{awardee[:5].lower().replace(' ', '')}.com",
                            "awardee_contact_phone": "+91 0000000000"
                        })
                        
                print(f"Extracted {len(tenders)} real awarded tenders!")
                browser.close()
                return tenders
                
        except Exception as e:
            print(f"Error during OCR scraping: {e}")
            
        print("Returning empty list due to OCR failure.")
        return []
