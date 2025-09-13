import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import os

class ESPNAPIClient:
    def __init__(self, db_path: str = "qb_database.db"):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
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
                week INTEGER,
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
                rushing_yards INTEGER,
                rushing_touchdowns INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (qb_id) REFERENCES quarterbacks (id),
                UNIQUE(qb_id, season, week)
            )
        ''')
        
        # Create seasons table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seasons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER UNIQUE,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized: {self.db_path}")
    
    def fetch_teams(self) -> List[Dict]:
        """Fetch all NFL teams from ESPN API"""
        try:
            url = f"{self.base_url}/teams"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams = []
            
            for sport in data.get('sports', []):
                for league in sport.get('leagues', []):
                    for team in league.get('teams', []):
                        team_info = team.get('team', {})
                        teams.append({
                            'id': team_info.get('id'),
                            'name': team_info.get('name'),
                            'abbreviation': team_info.get('abbreviation'),
                            'location': team_info.get('location'),
                            'displayName': team_info.get('displayName')
                        })
            
            return teams
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def fetch_team_roster(self, team_id: str) -> List[Dict]:
        """Fetch roster for a specific team"""
        try:
            url = f"{self.base_url}/teams/{team_id}/roster"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            players = []
            
            for athlete in data.get('athletes', []):
                player_info = athlete.get('athlete', {})
                position = player_info.get('position', {})
                
                if position.get('abbreviation') == 'QB':
                    players.append({
                        'id': player_info.get('id'),
                        'name': player_info.get('displayName'),
                        'team_id': team_id,
                        'position': 'QB',
                        'jersey': player_info.get('jersey'),
                        'age': player_info.get('age'),
                        'height': player_info.get('height'),
                        'weight': player_info.get('weight')
                    })
            
            return players
        except Exception as e:
            print(f"Error fetching roster for team {team_id}: {e}")
            return []
    
    def fetch_player_stats(self, player_id: str, season: int = None) -> Dict:
        """Fetch statistics for a specific player"""
        try:
            if season is None:
                season = datetime.now().year
            
            url = f"{self.base_url}/athletes/{player_id}/statistics"
            params = {'contentorigin': 'espn', 'year': season}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            stats = {}
            
            # Parse the statistics from the API response
            for split in data.get('splits', {}).get('categories', []):
                if split.get('name') == 'passing':
                    for stat in split.get('stats', []):
                        stat_name = stat.get('name')
                        stat_value = stat.get('value')
                        
                        if stat_name and stat_value is not None:
                            # Map ESPN stat names to our database columns
                            stat_mapping = {
                                'completions': 'completions',
                                'attempts': 'attempts',
                                'completionPct': 'completion_pct',
                                'passingYards': 'yards',
                                'yardsPerAttempt': 'yards_per_attempt',
                                'touchdowns': 'touchdowns',
                                'interceptions': 'interceptions',
                                'rating': 'rating',
                                'sacked': 'sacked',
                                'fumbles': 'fumbles'
                            }
                            
                            if stat_name in stat_mapping:
                                stats[stat_mapping[stat_name]] = stat_value
            
            return stats
        except Exception as e:
            print(f"Error fetching stats for player {player_id}: {e}")
            return {}
    
    def update_quarterbacks_database(self, season: int = None):
        """Update the database with current quarterback data"""
        if season is None:
            season = datetime.now().year
        
        print(f"Updating quarterback database for season {season}...")
        
        # Fetch all teams
        teams = self.fetch_teams()
        print(f"Found {len(teams)} teams")
        
        # Fetch quarterbacks from each team
        all_qbs = []
        for team in teams:
            print(f"Fetching roster for {team['displayName']}...")
            qbs = self.fetch_team_roster(team['id'])
            for qb in qbs:
                qb['team_name'] = team['displayName']
                qb['team_abbr'] = team['abbreviation']
            all_qbs.extend(qbs)
            time.sleep(1)  # Be respectful to the API
        
        print(f"Found {len(all_qbs)} quarterbacks")
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert/update quarterbacks
        for qb in all_qbs:
            cursor.execute('''
                INSERT OR REPLACE INTO quarterbacks (espn_id, name, team, position, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (qb['id'], qb['name'], qb['team_abbr'], qb['position'], datetime.now()))
        
        # Fetch and store stats for each quarterback
        for qb in all_qbs:
            print(f"Fetching stats for {qb['name']}...")
            stats = self.fetch_player_stats(qb['id'], season)
            
            if stats:
                # Get the qb_id from the database
                cursor.execute('SELECT id FROM quarterbacks WHERE espn_id = ?', (qb['id'],))
                result = cursor.fetchone()
                
                if result:
                    qb_id = result[0]
                    
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
                        datetime.now()
                    ))
            
            time.sleep(0.5)  # Be respectful to the API
        
        conn.commit()
        conn.close()
        print("Database update completed!")
    
    def get_quarterback_stats(self, season: int = None, min_attempts: int = 0) -> pd.DataFrame:
        """Get quarterback statistics from the database"""
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
            WHERE qs.season = ? AND qs.attempts >= ?
            ORDER BY qs.yards DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(season, min_attempts))
        conn.close()
        
        return df
    
    def get_quarterback_by_name(self, name: str, season: int = None) -> Optional[Dict]:
        """Get a specific quarterback's stats by name"""
        if season is None:
            season = datetime.now().year
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
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
                qs.fumbles
            FROM quarterbacks q
            JOIN quarterback_stats qs ON q.id = qs.qb_id
            WHERE q.name LIKE ? AND qs.season = ?
        ''', (f'%{name}%', season))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = ['name', 'team', 'games_played', 'completions', 'attempts', 
                      'completion_pct', 'yards', 'yards_per_attempt', 'touchdowns', 
                      'interceptions', 'rating', 'sacked', 'fumbles']
            return dict(zip(columns, result))
        
        return None
    
    def get_top_quarterbacks(self, stat: str = 'yards', limit: int = 10, season: int = None) -> List[Dict]:
        """Get top quarterbacks by a specific stat"""
        if season is None:
            season = datetime.now().year
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT 
                q.name,
                q.team,
                qs.{stat}
            FROM quarterbacks q
            JOIN quarterback_stats qs ON q.id = qs.qb_id
            WHERE qs.season = ?
            ORDER BY qs.{stat} DESC
            LIMIT ?
        ''', (season, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{'name': row[0], 'team': row[1], stat: row[2]} for row in results]
    
    def export_to_csv(self, filename: str = "qb_stats_from_db.csv", season: int = None):
        """Export quarterback stats to CSV"""
        df = self.get_quarterback_stats(season)
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
    
    def export_to_json(self, filename: str = "qb_stats_from_db.json", season: int = None):
        """Export quarterback stats to JSON"""
        df = self.get_quarterback_stats(season)
        data = df.to_dict('records')
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data exported to {filename}")

def main():
    """Example usage of the ESPN API client"""
    api_client = ESPNAPIClient()
    
    # Update the database with current data
    api_client.update_quarterbacks_database()
    
    # Get and display top quarterbacks
    top_qbs = api_client.get_top_quarterbacks('yards', 10)
    print("\nTop 10 Quarterbacks by Passing Yards:")
    for i, qb in enumerate(top_qbs, 1):
        print(f"{i}. {qb['name']} ({qb['team']}) - {qb['yards']} yards")
    
    # Export data
    api_client.export_to_csv()
    api_client.export_to_json()

if __name__ == "__main__":
    main()
