import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from typing import Dict, List, Optional

class ESPNQBScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        self.base_url = "https://www.espn.com"
    
    def fetch_qb_stats(self, season: str = "2024") -> Dict:
        """
        Fetch quarterback statistics from ESPN
        """
        try:
            # Try multiple ESPN URLs for quarterback stats
            urls_to_try = [
                f"{self.base_url}/nfl/stats/player/_/view/offense/stat/passing/table/passing/sort/passingYards/dir/desc",
                f"{self.base_url}/nfl/stats/player/_/stat/passing",
                f"{self.base_url}/nfl/stats/player/_/view/offense/stat/passing",
                f"{self.base_url}/nfl/stats/player/_/stat/passing/table/passing"
            ]
            
            for url in urls_to_try:
                print(f"Trying URL: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"Successfully accessed: {url}")
                    return self._parse_qb_stats(response.content)
                else:
                    print(f"Failed to access {url} (Status: {response.status_code})")
                    time.sleep(2)  # Wait before trying next URL
            
            # If all URLs fail, try with a different approach
            print("Trying alternative approach with ESPN's API...")
            return self._fetch_from_api()
            
        except requests.RequestException as e:
            print(f"Network error: {e}")
            return {}
        except Exception as e:
            print(f"Error fetching QB stats: {e}")
            return {}
    
    def _parse_qb_stats(self, content: bytes) -> Dict:
        """Parse quarterback statistics from HTML content"""
        soup = BeautifulSoup(content, 'html.parser')
        qb_stats = {}
        
        # Try multiple table selectors
        table_selectors = [
            'table.Table',
            'table',
            '.Table',
            '[class*="table"]',
            '[class*="stats"]'
        ]
        
        stats_table = None
        for selector in table_selectors:
            stats_table = soup.select_one(selector)
            if stats_table:
                print(f"Found table with selector: {selector}")
                break
        
        if not stats_table:
            print("Could not find stats table, trying to find any data...")
            # Look for any structured data
            return self._parse_alternative_data(soup)
        
        # Parse table rows
        rows = stats_table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 8:  # Ensure we have enough columns
                try:
                    # Extract player name and team
                    name_cell = cells[1] if len(cells) > 1 else cells[0]
                    name_link = name_cell.find('a')
                    if name_link:
                        name = name_link.get_text(strip=True)
                    else:
                        name = name_cell.get_text(strip=True)
                    
                    # Skip if name is empty or looks like a header
                    if not name or name.lower() in ['rank', 'player', 'team', '']:
                        continue
                    
                    # Extract team
                    team_cell = cells[2] if len(cells) > 2 else None
                    team = team_cell.get_text(strip=True) if team_cell else "N/A"
                    
                    # Extract statistics
                    stats = {
                        'team': team,
                        'games_played': self._extract_number(cells[3]) if len(cells) > 3 else 0,
                        'completions': self._extract_number(cells[4]) if len(cells) > 4 else 0,
                        'attempts': self._extract_number(cells[5]) if len(cells) > 5 else 0,
                        'completion_pct': self._extract_number(cells[6]) if len(cells) > 6 else 0,
                        'yards': self._extract_number(cells[7]) if len(cells) > 7 else 0,
                        'yards_per_attempt': self._extract_number(cells[8]) if len(cells) > 8 else 0,
                        'touchdowns': self._extract_number(cells[9]) if len(cells) > 9 else 0,
                        'interceptions': self._extract_number(cells[10]) if len(cells) > 10 else 0,
                        'rating': self._extract_number(cells[11]) if len(cells) > 11 else 0,
                    }
                    
                    qb_stats[name] = stats
                    
                except (IndexError, AttributeError) as e:
                    print(f"Error parsing row: {e}")
                    continue
        
        print(f"Successfully parsed {len(qb_stats)} quarterbacks")
        return qb_stats
    
    def _parse_alternative_data(self, soup: BeautifulSoup) -> Dict:
        """Parse data using alternative methods when table parsing fails"""
        qb_stats = {}
        
        # Look for script tags with JSON data
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'window.espn.scoreboardData' in script.string:
                print("Found ESPN data in script tag")
                # This would require more complex parsing
                break
        
        # Look for any divs with player data
        player_divs = soup.find_all('div', class_=lambda x: x and ('player' in x.lower() or 'qb' in x.lower()))
        
        if not player_divs:
            print("No alternative data found")
            return {}
        
        return qb_stats
    
    def _fetch_from_api(self) -> Dict:
        """Try to fetch data from ESPN's API endpoints"""
        try:
            # ESPN might have API endpoints we can use
            api_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/statistics"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("Successfully fetched data from ESPN API")
                return self._parse_api_data(data)
            else:
                print(f"API request failed with status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"API fetch error: {e}")
            return {}
    
    def _parse_api_data(self, data: Dict) -> Dict:
        """Parse data from ESPN's API response"""
        qb_stats = {}
        
        # This would need to be implemented based on ESPN's actual API structure
        # For now, return empty dict
        return qb_stats
    
    def _extract_number(self, cell) -> float:
        """Extract numeric value from table cell"""
        if not cell:
            return 0.0
        
        text = cell.get_text(strip=True)
        if not text or text == '-':
            return 0.0
        
        # Remove any non-numeric characters except decimal points
        cleaned = ''.join(c for c in text if c.isdigit() or c == '.')
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def search_qb_by_name(self, qb_stats: Dict, search_name: str) -> Optional[Dict]:
        """Search for a quarterback by name (case-insensitive)"""
        search_name_lower = search_name.lower()
        
        for name, stats in qb_stats.items():
            if search_name_lower in name.lower():
                return {name: stats}
        
        return None
    
    def get_top_qbs(self, qb_stats: Dict, stat: str = 'yards', limit: int = 10) -> List[tuple]:
        """Get top quarterbacks by a specific stat"""
        if not qb_stats:
            return []
        
        sorted_qbs = sorted(
            qb_stats.items(),
            key=lambda x: x[1].get(stat, 0),
            reverse=True
        )
        
        return sorted_qbs[:limit]
    
    def save_to_csv(self, qb_stats: Dict, filename: str = "qb_stats.csv"):
        """Save quarterback stats to CSV file"""
        if not qb_stats:
            print("No data to save")
            return
        
        df = pd.DataFrame.from_dict(qb_stats, orient='index')
        df.index.name = 'quarterback'
        df.to_csv(filename)
        print(f"Data saved to {filename}")
    
    def save_to_json(self, qb_stats: Dict, filename: str = "qb_stats.json"):
        """Save quarterback stats to JSON file"""
        if not qb_stats:
            print("No data to save")
            return
        
        with open(filename, 'w') as f:
            json.dump(qb_stats, f, indent=2)
        print(f"Data saved to {filename}")

def main():
    scraper = ESPNQBScraper()
    
    # Fetch quarterback statistics
    print("Fetching quarterback statistics from ESPN...")
    qb_stats = scraper.fetch_qb_stats()
    
    if not qb_stats:
        print("Failed to fetch quarterback statistics")
        print("This might be due to ESPN's anti-bot measures.")
        print("You can try:")
        print("1. Using a VPN")
        print("2. Waiting a few minutes and trying again")
        print("3. Using the demo data feature")
        
        # Create some demo data for testing
        demo_data = {
            "Patrick Mahomes": {
                "team": "KC",
                "games_played": 17,
                "completions": 362,
                "attempts": 565,
                "completion_pct": 64.1,
                "yards": 4183,
                "yards_per_attempt": 7.4,
                "touchdowns": 31,
                "interceptions": 8,
                "rating": 105.2
            },
            "Josh Allen": {
                "team": "BUF",
                "games_played": 17,
                "completions": 359,
                "attempts": 565,
                "completion_pct": 63.5,
                "yards": 4306,
                "yards_per_attempt": 7.6,
                "touchdowns": 35,
                "interceptions": 14,
                "rating": 92.6
            },
            "Justin Herbert": {
                "team": "LAC",
                "games_played": 13,
                "completions": 313,
                "attempts": 477,
                "completion_pct": 65.6,
                "yards": 3104,
                "yards_per_attempt": 6.5,
                "touchdowns": 20,
                "interceptions": 7,
                "rating": 93.2
            }
        }
        
        print("\nUsing demo data for testing...")
        qb_stats = demo_data
    
    # Display top 10 QBs by passing yards
    print("\n=== Top Quarterbacks by Passing Yards ===")
    top_qbs = scraper.get_top_qbs(qb_stats, 'yards', 10)
    for i, (name, stats) in enumerate(top_qbs, 1):
        print(f"{i}. {name} ({stats['team']}) - {stats['yards']} yards, {stats['touchdowns']} TD, {stats['interceptions']} INT")
    
    # Save data
    scraper.save_to_csv(qb_stats)
    scraper.save_to_json(qb_stats)
    
    return qb_stats

if __name__ == "__main__":
    main()