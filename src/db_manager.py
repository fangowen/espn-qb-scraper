import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from espn_api import ESPNAPIClient

class DatabaseManager:
    def __init__(self, db_path: str = "qb_database.db"):
        self.db_path = db_path
        self.api_client = ESPNAPIClient(db_path)
        
    def needs_update(self, max_age_hours: int = 24) -> bool:
        """Check if the database needs to be updated"""
        if not os.path.exists(self.db_path):
            return True
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check when the database was last updated
        cursor.execute('''
            SELECT MAX(last_updated) FROM quarterback_stats
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return True
        
        last_updated = datetime.fromisoformat(result[0].replace('Z', '+00:00'))
        age = datetime.now() - last_updated.replace(tzinfo=None)
        
        return age.total_seconds() > (max_age_hours * 3600)
    
    def update_database(self, force: bool = False):
        """Update the database with fresh data from ESPN"""
        if force or self.needs_update():
            print("Updating database with fresh data from ESPN...")
            self.api_client.update_quarterbacks_database()
        else:
            print("Database is up to date")
    
    def get_all_quarterbacks(self, season: int = None, min_attempts: int = 0) -> Dict[str, Dict]:
        """Get all quarterback statistics as a dictionary"""
        df = self.api_client.get_quarterback_stats(season, min_attempts)
        
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
    
    def get_quarterback(self, name: str, season: int = None) -> Optional[Dict]:
        """Get a specific quarterback's statistics"""
        return self.api_client.get_quarterback_by_name(name, season)
    
    def get_top_quarterbacks(self, stat: str = 'yards', limit: int = 10, season: int = None) -> List[Dict]:
        """Get top quarterbacks by a specific statistic"""
        return self.api_client.get_top_quarterbacks(stat, limit, season)
    
    def search_quarterbacks(self, search_term: str, season: int = None) -> List[Dict]:
        """Search for quarterbacks by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                q.name,
                q.team,
                qs.games_played,
                qs.yards,
                qs.touchdowns,
                qs.interceptions,
                qs.rating
            FROM quarterbacks q
            JOIN quarterback_stats qs ON q.id = qs.qb_id
            WHERE q.name LIKE ? AND qs.season = ?
            ORDER BY qs.yards DESC
        ''', (f'%{search_term}%', season or datetime.now().year))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': row[0],
                'team': row[1],
                'games_played': row[2],
                'yards': row[3],
                'touchdowns': row[4],
                'interceptions': row[5],
                'rating': row[6]
            }
            for row in results
        ]
    
    def get_database_info(self) -> Dict:
        """Get information about the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get quarterback count
        cursor.execute('SELECT COUNT(*) FROM quarterbacks')
        qb_count = cursor.fetchone()[0]
        
        # Get stats count
        cursor.execute('SELECT COUNT(*) FROM quarterback_stats')
        stats_count = cursor.fetchone()[0]
        
        # Get last update time
        cursor.execute('SELECT MAX(last_updated) FROM quarterback_stats')
        last_updated = cursor.fetchone()[0]
        
        # Get available seasons
        cursor.execute('SELECT DISTINCT season FROM quarterback_stats ORDER BY season DESC')
        seasons = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'quarterback_count': qb_count,
            'stats_records': stats_count,
            'last_updated': last_updated,
            'available_seasons': seasons
        }
    
    def export_data(self, format: str = 'json', filename: str = None, season: int = None):
        """Export data in various formats"""
        if format.lower() == 'csv':
            if not filename:
                filename = f"qb_stats_{season or 'current'}.csv"
            self.api_client.export_to_csv(filename, season)
        elif format.lower() == 'json':
            if not filename:
                filename = f"qb_stats_{season or 'current'}.json"
            self.api_client.export_to_json(filename, season)
        else:
            raise ValueError("Format must be 'csv' or 'json'")
    
    def get_comparison_data(self, qb_names: List[str], season: int = None) -> pd.DataFrame:
        """Get comparison data for multiple quarterbacks"""
        conn = sqlite3.connect(self.db_path)
        
        placeholders = ','.join(['?' for _ in qb_names])
        query = f'''
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
            WHERE q.name IN ({placeholders}) AND qs.season = ?
            ORDER BY qs.yards DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=qb_names + [season or datetime.now().year])
        conn.close()
        
        return df
    
    def get_team_quarterbacks(self, team_abbr: str, season: int = None) -> List[Dict]:
        """Get all quarterbacks for a specific team"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                q.name,
                qs.games_played,
                qs.yards,
                qs.touchdowns,
                qs.interceptions,
                qs.rating,
                qs.completion_pct
            FROM quarterbacks q
            JOIN quarterback_stats qs ON q.id = qs.qb_id
            WHERE q.team = ? AND qs.season = ?
            ORDER BY qs.yards DESC
        ''', (team_abbr.upper(), season or datetime.now().year))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'name': row[0],
                'games_played': row[1],
                'yards': row[2],
                'touchdowns': row[3],
                'interceptions': row[4],
                'rating': row[5],
                'completion_pct': row[6]
            }
            for row in results
        ]

def main():
    """Example usage of the DatabaseManager"""
    db_manager = DatabaseManager()
    
    # Check if database needs update
    if db_manager.needs_update():
        print("Database needs update, fetching fresh data...")
        db_manager.update_database()
    else:
        print("Database is up to date")
    
    # Get database info
    info = db_manager.get_database_info()
    print(f"\nDatabase Info:")
    print(f"Quarterbacks: {info['quarterback_count']}")
    print(f"Stats records: {info['stats_records']}")
    print(f"Last updated: {info['last_updated']}")
    print(f"Available seasons: {info['available_seasons']}")
    
    # Get top quarterbacks
    top_qbs = db_manager.get_top_quarterbacks('yards', 5)
    print(f"\nTop 5 Quarterbacks by Passing Yards:")
    for i, qb in enumerate(top_qbs, 1):
        print(f"{i}. {qb['name']} ({qb['team']}) - {qb['yards']} yards")
    
    # Export data
    db_manager.export_data('json', 'qb_stats_export.json')

if __name__ == "__main__":
    main()
