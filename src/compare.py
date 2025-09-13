import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns

class QuarterbackComparer:
    def __init__(self, qb_data: Dict):
        self.qb_data = qb_data
        self.stats_columns = [
            'yards', 'touchdowns', 'interceptions', 'completion_pct', 
            'rating', 'yards_per_attempt', 'games_played'
        ]
    
    def compare_stats(self, qb1_name: str, qb2_name: str) -> Dict:
        """Compare two quarterbacks head-to-head"""
        qb1_stats = self._find_qb(qb1_name)
        qb2_stats = self._find_qb(qb2_name)
        
        if not qb1_stats or not qb2_stats:
            return {"error": "One or both quarterbacks not found"}
        
        comparison = {
            "quarterback_1": {"name": qb1_name, "stats": qb1_stats},
            "quarterback_2": {"name": qb2_name, "stats": qb2_stats},
            "comparisons": {}
        }
        
        # Compare each stat
        for stat in self.stats_columns:
            if stat in qb1_stats and stat in qb2_stats:
                val1 = qb1_stats[stat]
                val2 = qb2_stats[stat]
                
                if val1 > val2:
                    winner = qb1_name
                    difference = val1 - val2
                elif val2 > val1:
                    winner = qb2_name
                    difference = val2 - val1
                else:
                    winner = "Tie"
                    difference = 0
                
                comparison["comparisons"][stat] = {
                    "qb1_value": val1,
                    "qb2_value": val2,
                    "winner": winner,
                    "difference": difference
                }
        
        return comparison
    
    def _find_qb(self, search_name: str) -> Optional[Dict]:
        """Find quarterback by name (case-insensitive partial match)"""
        search_name_lower = search_name.lower()
        
        for name, stats in self.qb_data.items():
            if search_name_lower in name.lower():
                return stats
        
        return None
    
    def get_best_qb(self, stat: str = 'yards') -> Tuple[str, Dict]:
        """Get the quarterback with the best performance in a specific stat"""
        if not self.qb_data:
            return None, {}
        
        best_qb = max(self.qb_data.items(), key=lambda item: item[1].get(stat, 0))
        return best_qb[0], best_qb[1]
    
    def get_top_qbs(self, stat: str = 'yards', limit: int = 5) -> List[Tuple[str, Dict]]:
        """Get top quarterbacks by a specific stat"""
        if not self.qb_data:
            return []
        
        sorted_qbs = sorted(
            self.qb_data.items(),
            key=lambda x: x[1].get(stat, 0),
            reverse=True
        )
        
        return sorted_qbs[:limit]
    
    def compare_multiple_qbs(self, qb_names: List[str], stats: List[str] = None) -> pd.DataFrame:
        """Compare multiple quarterbacks in a table format"""
        if stats is None:
            stats = self.stats_columns
        
        comparison_data = []
        
        for qb_name in qb_names:
            qb_stats = self._find_qb(qb_name)
            if qb_stats:
                row = {'quarterback': qb_name}
                for stat in stats:
                    row[stat] = qb_stats.get(stat, 0)
                comparison_data.append(row)
        
        return pd.DataFrame(comparison_data)
    
    def get_qb_summary(self, qb_name: str) -> Dict:
        """Get a comprehensive summary for a specific quarterback"""
        qb_stats = self._find_qb(qb_name)
        if not qb_stats:
            return {"error": f"Quarterback '{qb_name}' not found"}
        
        # Calculate additional metrics
        if qb_stats.get('attempts', 0) > 0:
            td_int_ratio = qb_stats.get('touchdowns', 0) / max(qb_stats.get('interceptions', 1), 1)
        else:
            td_int_ratio = 0
        
        summary = {
            "name": qb_name,
            "team": qb_stats.get('team', 'N/A'),
            "games_played": qb_stats.get('games_played', 0),
            "passing_yards": qb_stats.get('yards', 0),
            "touchdowns": qb_stats.get('touchdowns', 0),
            "interceptions": qb_stats.get('interceptions', 0),
            "completion_percentage": qb_stats.get('completion_pct', 0),
            "passer_rating": qb_stats.get('rating', 0),
            "yards_per_attempt": qb_stats.get('yards_per_attempt', 0),
            "td_to_int_ratio": round(td_int_ratio, 2)
        }
        
        return summary
    
    def print_comparison(self, qb1_name: str, qb2_name: str):
        """Print a formatted comparison between two quarterbacks"""
        comparison = self.compare_stats(qb1_name, qb2_name)
        
        if "error" in comparison:
            print(f"Error: {comparison['error']}")
            return
        
        qb1 = comparison["quarterback_1"]
        qb2 = comparison["quarterback_2"]
        
        print(f"\n{'='*60}")
        print(f"QUARTERBACK COMPARISON")
        print(f"{'='*60}")
        print(f"{qb1['name']} ({qb1['stats']['team']}) vs {qb2['name']} ({qb2['stats']['team']})")
        print(f"{'='*60}")
        
        for stat, comp in comparison["comparisons"].items():
            stat_name = stat.replace('_', ' ').title()
            print(f"{stat_name:20} | {comp['qb1_value']:>8} | {comp['qb2_value']:>8} | {comp['winner']:>10}")
        
        print(f"{'='*60}")
    
    def print_top_qbs(self, stat: str = 'yards', limit: int = 10):
        """Print top quarterbacks by a specific stat"""
        top_qbs = self.get_top_qbs(stat, limit)
        
        stat_name = stat.replace('_', ' ').title()
        print(f"\n{'='*50}")
        print(f"TOP {limit} QUARTERBACKS BY {stat_name.upper()}")
        print(f"{'='*50}")
        
        for i, (name, stats) in enumerate(top_qbs, 1):
            team = stats.get('team', 'N/A')
            value = stats.get(stat, 0)
            print(f"{i:2}. {name:25} ({team:3}) - {value:>8}")
        
        print(f"{'='*50}")

def main():
    """Example usage of the QuarterbackComparer"""
    # This would typically be used with data from the scraper
    print("QuarterbackComparer initialized. Use with scraped data from ESPNQBScraper.")
    print("Example usage:")
    print("1. scraper = ESPNQBScraper()")
    print("2. qb_data = scraper.fetch_qb_stats()")
    print("3. comparer = QuarterbackComparer(qb_data)")
    print("4. comparer.compare_stats('Patrick Mahomes', 'Josh Allen')")

if __name__ == "__main__":
    main()