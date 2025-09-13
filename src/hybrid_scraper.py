import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
import os

class HybridQBScraper:
    def __init__(self, db_path: str = "qb_database.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create quarterbacks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quarterbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                espn_id TEXT UNIQUE,
                name TEXT NOT NULL,
                team TEXT,
                position TEXT DEFAULT 'QB',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create quarterback_stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quarterback_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qb_id INTEGER,
                season INTEGER,
                games_played INTEGER,
                completions INTEGER,
                attempts INTEGER,
                completion_pct REAL,
                yards INTEGER,
                yards_per_attempt REAL,
                touchdowns INTEGER,
                interceptions INTEGER,
                rating REAL,
                sacked INTEGER,
                fumbles INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (qb_id) REFERENCES quarterbacks (id),
                UNIQUE(qb_id, season)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def get_demo_data(self) -> Dict[str, Dict]:
        """Get comprehensive demo data for testing"""
        return {
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
                "rating": 105.2,
                "sacked": 28,
                "fumbles": 3
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
                "rating": 92.6,
                "sacked": 24,
                "fumbles": 5
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
                "rating": 93.2,
                "sacked": 29,
                "fumbles": 4
            },
            "Lamar Jackson": {
                "team": "BAL",
                "games_played": 16,
                "completions": 307,
                "attempts": 457,
                "completion_pct": 67.2,
                "yards": 3678,
                "yards_per_attempt": 8.0,
                "touchdowns": 24,
                "interceptions": 7,
                "rating": 102.7,
                "sacked": 19,
                "fumbles": 6
            },
            "Joe Burrow": {
                "team": "CIN",
                "games_played": 10,
                "completions": 244,
                "attempts": 365,
                "completion_pct": 66.8,
                "yards": 2309,
                "yards_per_attempt": 6.3,
                "touchdowns": 15,
                "interceptions": 6,
                "rating": 91.0,
                "sacked": 24,
                "fumbles": 2
            },
            "Dak Prescott": {
                "team": "DAL",
                "games_played": 17,
                "completions": 410,
                "attempts": 590,
                "completion_pct": 69.5,
                "yards": 4516,
                "yards_per_attempt": 7.7,
                "touchdowns": 36,
                "interceptions": 9,
                "rating": 105.9,
                "sacked": 39,
                "fumbles": 7
            },
            "Jalen Hurts": {
                "team": "PHI",
                "games_played": 17,
                "completions": 352,
                "attempts": 538,
                "completion_pct": 65.4,
                "yards": 3858,
                "yards_per_attempt": 7.2,
                "touchdowns": 23,
                "interceptions": 15,
                "rating": 89.1,
                "sacked": 38,
                "fumbles": 8
            },
            "Tua Tagovailoa": {
                "team": "MIA",
                "games_played": 17,
                "completions": 388,
                "attempts": 560,
                "completion_pct": 69.3,
                "yards": 4624,
                "yards_per_attempt": 8.3,
                "touchdowns": 29,
                "interceptions": 14,
                "rating": 101.1,
                "sacked": 34,
                "fumbles": 4
            },
            "Kirk Cousins": {
                "team": "MIN",
                "games_played": 8,
                "completions": 216,
                "attempts": 311,
                "completion_pct": 69.5,
                "yards": 2331,
                "yards_per_attempt": 7.5,
                "touchdowns": 18,
                "interceptions": 5,
                "rating": 103.8,
                "sacked": 16,
                "fumbles": 2
            },
            "Jared Goff": {
                "team": "DET",
                "games_played": 17,
                "completions": 407,
                "attempts": 605,
                "completion_pct": 67.3,
                "yards": 4575,
                "yards_per_attempt": 7.6,
                "touchdowns": 30,
                "interceptions": 12,
                "rating": 97.9,
                "sacked": 30,
                "fumbles": 5
            }
        }
    
    def try_espn_api(self) -> Dict[str, Dict]:
        """Try to fetch data from ESPN API"""
        try:
            print("Trying ESPN API...")
            
            # Try the statistics endpoint
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/statistics"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("Successfully accessed ESPN API")
                
                # Parse the statistics data
                return self._parse_api_stats(data)
            else:
                print(f"API request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"API error: {e}")
            return {}
    
    def _parse_api_stats(self, data: Dict) -> Dict[str, Dict]:
        """Parse statistics from ESPN API response"""
        qb_stats = {}
        
        # This is a simplified parser - the actual ESPN API structure may vary
        # For now, return empty dict and rely on demo data
        return qb_stats
    
    def try_web_scraping(self) -> Dict[str, Dict]:
        """Try to scrape data from ESPN website"""
        try:
            print("Trying web scraping...")
            
            urls_to_try = [
                "https://www.espn.com/nfl/stats/player/_/view/offense/stat/passing/table/passing/sort/passingYards/dir/desc",
                "https://www.espn.com/nfl/stats/player/_/stat/passing",
                "https://www.espn.com/nfl/stats/player/_/view/offense/stat/passing"
            ]
            
            for url in urls_to_try:
                print(f"Trying URL: {url}")
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    print(f"Successfully accessed: {url}")
                    return self._parse_webpage(response.content)
                else:
                    print(f"Failed to access {url} (Status: {response.status_code})")
                    time.sleep(2)
            
            return {}
            
        except Exception as e:
            print(f"Web scraping error: {e}")
            return {}
    
    def _parse_webpage(self, content: bytes) -> Dict[str, Dict]:
        """Parse quarterback data from webpage"""
        soup = BeautifulSoup(content, 'html.parser')
        qb_stats = {}
        
        # Try to find stats table
        table_selectors = ['table.Table', 'table', '.Table', '[class*="table"]']
        
        for selector in table_selectors:
            table = soup.select_one(selector)
            if table:
                print(f"Found table with selector: {selector}")
                # Parse table data
                # This would need to be implemented based on actual HTML structure
                break
        
        return qb_stats
    
    def update_database(self, force_demo: bool = False):
        """Update database with quarterback data"""
        print("Updating quarterback database...")
        
        # Try different data sources
        qb_data = {}
        
        if not force_demo:
            # Try API first
            qb_data = self.try_espn_api()
            
            # If API fails, try web scraping
            if not qb_data:
                qb_data = self.try_web_scraping()
        
        # If all else fails, use demo data
        if not qb_data:
            print("Using demo data...")
            qb_data = self.get_demo_data()
        
        # Save to database
        self._save_to_database(qb_data)
        
        print(f"Database updated with {len(qb_data)} quarterbacks")
        return qb_data
    
    def _save_to_database(self, qb_data: Dict[str, Dict]):
        """Save quarterback data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now()
        season = datetime.now().year
        
        for name, stats in qb_data.items():
            # Insert/update quarterback
            cursor.execute('''
                INSERT OR REPLACE INTO quarterbacks (espn_id, name, team, position, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (f"demo_{name.lower().replace(' ', '_')}", name, stats['team'], 'QB', current_time))
            
            # Get qb_id
            cursor.execute('SELECT id FROM quarterbacks WHERE espn_id = ?', (f"demo_{name.lower().replace(' ', '_')}",))
            qb_id = cursor.fetchone()[0]
            
            # Insert/update stats
            cursor.execute('''
                INSERT OR REPLACE INTO quarterback_stats 
                (qb_id, season, games_played, completions, attempts, completion_pct, 
                 yards, yards_per_attempt, touchdowns, interceptions, rating, 
                 sacked, fumbles, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                qb_id, season,
                stats.get('games_played', 0),
                stats.get('completions', 0),
                stats.get('attempts', 0),
                stats.get('completion_pct', 0),
                stats.get('yards', 0),
                stats.get('yards_per_attempt', 0),
                stats.get('touchdowns', 0),
                stats.get('interceptions', 0),
                stats.get('rating', 0),
                stats.get('sacked', 0),
                stats.get('fumbles', 0),
                current_time
            ))
        
        conn.commit()
        conn.close()
    
    def get_quarterback_stats(self, season: int = None) -> pd.DataFrame:
        """Get quarterback statistics from database"""
        if season is None:
            season = datetime.now().year
        
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                q.name,
                q.team,
                qs.games_played,
                qs.completions,
                qs.attempts,
                qs.completion_pct,
                qs.yards,
                qs.yards_per_attempt,
                qs.touchdowns,
                qs.interceptions,
                qs.rating,
                qs.sacked,
                qs.fumbles,
                qs.last_updated
            FROM quarterbacks q
            JOIN quarterback_stats qs ON q.id = qs.qb_id
            WHERE qs.season = ?
            ORDER BY qs.yards DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(season,))
        conn.close()
        
        return df
    
    def get_all_quarterbacks(self, season: int = None) -> Dict[str, Dict]:
        """Get all quarterback statistics as a dictionary"""
        df = self.get_quarterback_stats(season)
        
        qb_dict = {}
        for _, row in df.iterrows():
            qb_dict[row['name']] = {
                'team': row['team'],
                'games_played': int(row['games_played']),
                'completions': int(row['completions']),
                'attempts': int(row['attempts']),
                'completion_pct': float(row['completion_pct']),
                'yards': int(row['yards']),
                'yards_per_attempt': float(row['yards_per_attempt']),
                'touchdowns': int(row['touchdowns']),
                'interceptions': int(row['interceptions']),
                'rating': float(row['rating']),
                'sacked': int(row['sacked']) if pd.notna(row['sacked']) else 0,
                'fumbles': int(row['fumbles']) if pd.notna(row['fumbles']) else 0
            }
        
        return qb_dict
    
    def export_to_csv(self, filename: str = "qb_stats_hybrid.csv", season: int = None):
        """Export quarterback stats to CSV"""
        df = self.get_quarterback_stats(season)
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
    
    def export_to_json(self, filename: str = "qb_stats_hybrid.json", season: int = None):
        """Export quarterback stats to JSON"""
        qb_data = self.get_all_quarterbacks(season)
        
        with open(filename, 'w') as f:
            json.dump(qb_data, f, indent=2)
        print(f"Data exported to {filename}")

def main():
    """Example usage of the HybridQBScraper"""
    scraper = HybridQBScraper()
    
    # Update database
    qb_data = scraper.update_database()
    
    # Display top quarterbacks
    print("\n=== Top Quarterbacks by Passing Yards ===")
    sorted_qbs = sorted(qb_data.items(), key=lambda x: x[1]['yards'], reverse=True)
    
    for i, (name, stats) in enumerate(sorted_qbs[:10], 1):
        print(f"{i}. {name} ({stats['team']}) - {stats['yards']} yards, {stats['touchdowns']} TD, {stats['interceptions']} INT")
    
    # Export data
    scraper.export_to_csv()
    scraper.export_to_json()

if __name__ == "__main__":
    main()
