import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class FantasyFootballAnalyzer:
    def __init__(self, qb_data: Dict[str, Dict]):
        self.qb_data = qb_data
        self.standard_scoring = {
            'passing_yards': 0.04,      # 1 point per 25 yards
            'passing_touchdowns': 4,    # 4 points per TD
            'interceptions': -2,        # -2 points per INT
            'rushing_yards': 0.1,       # 1 point per 10 yards
            'rushing_touchdowns': 6,    # 6 points per rushing TD
            'fumbles_lost': -2,         # -2 points per fumble lost
            'passing_2pt': 2,           # 2 points per 2pt conversion
            'rushing_2pt': 2            # 2 points per rushing 2pt conversion
        }
        
        # Calculate fantasy points for all quarterbacks
        self.calculate_all_fantasy_points()
    
    def calculate_fantasy_points(self, qb_stats: Dict, scoring: Dict = None) -> float:
        """Calculate fantasy points for a quarterback"""
        if scoring is None:
            scoring = self.standard_scoring
        
        points = 0
        
        # Passing stats
        points += qb_stats.get('yards', 0) * scoring['passing_yards']
        points += qb_stats.get('touchdowns', 0) * scoring['passing_touchdowns']
        points += qb_stats.get('interceptions', 0) * scoring['interceptions']
        
        # Rushing stats (if available)
        points += qb_stats.get('rushing_yards', 0) * scoring['rushing_yards']
        points += qb_stats.get('rushing_touchdowns', 0) * scoring['rushing_touchdowns']
        
        # Other stats
        points += qb_stats.get('fumbles', 0) * scoring['fumbles_lost']
        
        return round(points, 2)
    
    def calculate_all_fantasy_points(self):
        """Calculate fantasy points for all quarterbacks"""
        for qb_name, stats in self.qb_data.items():
            total_points = self.calculate_fantasy_points(stats)
            avg_points = total_points / stats.get('games_played', 1)
            
            # Add fantasy stats to the quarterback data
            stats['fantasy_points_total'] = total_points
            stats['fantasy_points_avg'] = round(avg_points, 2)
    
    def get_fantasy_rankings(self, top_n: int = 20) -> List[Dict]:
        """Get fantasy football rankings for quarterbacks"""
        rankings = []
        
        for qb_name, stats in self.qb_data.items():
            rankings.append({
                'rank': 0,  # Will be set below
                'name': qb_name,
                'team': stats['team'],
                'fantasy_points_total': stats['fantasy_points_total'],
                'fantasy_points_avg': stats['fantasy_points_avg'],
                'games_played': stats['games_played'],
                'yards': stats['yards'],
                'touchdowns': stats['touchdowns'],
                'interceptions': stats['interceptions']
            })
        
        # Sort by average fantasy points
        rankings.sort(key=lambda x: x['fantasy_points_avg'], reverse=True)
        
        # Add rankings
        for i, qb in enumerate(rankings[:top_n], 1):
            qb['rank'] = i
        
        return rankings[:top_n]
    
    def get_start_sit_recommendations(self) -> Dict[str, List]:
        """Generate start/sit recommendations based on fantasy performance"""
        recommendations = {
            'must_start': [],
            'good_start': [],
            'flex_start': [],
            'sit': []
        }
        
        for qb_name, stats in self.qb_data.items():
            avg_points = stats['fantasy_points_avg']
            
            if avg_points >= 20:
                recommendations['must_start'].append({
                    'name': qb_name,
                    'team': stats['team'],
                    'avg_points': avg_points,
                    'reason': 'Elite fantasy producer'
                })
            elif avg_points >= 15:
                recommendations['good_start'].append({
                    'name': qb_name,
                    'team': stats['team'],
                    'avg_points': avg_points,
                    'reason': 'Solid fantasy starter'
                })
            elif avg_points >= 10:
                recommendations['flex_start'].append({
                    'name': qb_name,
                    'team': stats['team'],
                    'avg_points': avg_points,
                    'reason': 'Flexible starter option'
                })
            else:
                recommendations['sit'].append({
                    'name': qb_name,
                    'team': stats['team'],
                    'avg_points': avg_points,
                    'reason': 'Bench or stream only'
                })
        
        return recommendations
    
    def get_weekly_projections(self, week: int = None) -> Dict[str, Dict]:
        """Generate weekly fantasy projections"""
        projections = {}
        
        for qb_name, stats in self.qb_data.items():
            # Simple projection based on season averages
            avg_yards = stats['yards'] / stats['games_played']
            avg_tds = stats['touchdowns'] / stats['games_played']
            avg_ints = stats['interceptions'] / stats['games_played']
            
            # Add some variance for realistic projections
            import random
            yards_variance = random.uniform(0.8, 1.2)
            tds_variance = random.uniform(0.7, 1.3)
            
            projected_yards = int(avg_yards * yards_variance)
            projected_tds = round(avg_tds * tds_variance, 1)
            projected_ints = round(avg_ints, 1)
            
            projected_stats = {
                'passing_yards': projected_yards,
                'touchdowns': projected_tds,
                'interceptions': projected_ints
            }
            
            projected_points = self.calculate_fantasy_points(projected_stats)
            
            projections[qb_name] = {
                'team': stats['team'],
                'projected_yards': projected_yards,
                'projected_touchdowns': projected_tds,
                'projected_interceptions': projected_ints,
                'projected_points': projected_points,
                'confidence': 'High' if stats['games_played'] >= 10 else 'Medium'
            }
        
        return projections
    
    def analyze_trade_value(self, qb1_name: str, qb2_name: str) -> Optional[Dict]:
        """Analyze trade value between two quarterbacks"""
        qb1_stats = self.qb_data.get(qb1_name)
        qb2_stats = self.qb_data.get(qb2_name)
        
        if not qb1_stats or not qb2_stats:
            return None
        
        qb1_avg = qb1_stats['fantasy_points_avg']
        qb2_avg = qb2_stats['fantasy_points_avg']
        
        point_diff = qb1_avg - qb2_avg
        
        if abs(point_diff) < 2:
            recommendation = "Fair trade - similar value"
        elif point_diff > 5:
            recommendation = f"Trade for {qb1_name} - significantly better"
        elif point_diff < -5:
            recommendation = f"Trade for {qb2_name} - significantly better"
        else:
            recommendation = f"Trade for {qb1_name if point_diff > 0 else qb2_name} - slight advantage"
        
        return {
            'qb1': {
                'name': qb1_name,
                'team': qb1_stats['team'],
                'avg_points': qb1_avg,
                'total_points': qb1_stats['fantasy_points_total']
            },
            'qb2': {
                'name': qb2_name,
                'team': qb2_stats['team'],
                'avg_points': qb2_avg,
                'total_points': qb2_stats['fantasy_points_total']
            },
            'point_difference': round(point_diff, 2),
            'recommendation': recommendation
        }
    
    def get_waiver_wire_targets(self, ownership_data: Dict[str, int] = None) -> List[Dict]:
        """Identify waiver wire targets"""
        if ownership_data is None:
            # Mock ownership data - in real implementation, you'd get this from fantasy platform
            ownership_data = {
                'Patrick Mahomes': 95,
                'Josh Allen': 92,
                'Justin Herbert': 88,
                'Lamar Jackson': 85,
                'Joe Burrow': 82,
                'Dak Prescott': 78,
                'Jalen Hurts': 75,
                'Tua Tagovailoa': 70,
                'Jared Goff': 65,
                'Kirk Cousins': 60
            }
        
        waiver_targets = []
        
        for qb_name, stats in self.qb_data.items():
            ownership = ownership_data.get(qb_name, 50)  # Default to 50% if not found
            avg_points = stats['fantasy_points_avg']
            
            if ownership < 70 and avg_points >= 12:  # Less than 70% owned and good producer
                waiver_targets.append({
                    'name': qb_name,
                    'team': stats['team'],
                    'avg_points': avg_points,
                    'ownership': ownership,
                    'priority': 'High' if avg_points >= 15 else 'Medium',
                    'reason': f"Only {ownership}% owned, averaging {avg_points} points"
                })
        
        return sorted(waiver_targets, key=lambda x: x['avg_points'], reverse=True)
    
    def get_strength_of_schedule(self, qb_name: str, remaining_weeks: int = 5) -> Dict:
        """Analyze strength of schedule for a quarterback"""
        # This would require additional data about opponent defenses
        # For now, return a mock analysis
        return {
            'qb_name': qb_name,
            'remaining_weeks': remaining_weeks,
            'difficulty': 'Medium',  # Easy, Medium, Hard
            'favorable_matchups': 2,
            'tough_matchups': 1,
            'neutral_matchups': 2,
            'recommendation': 'Hold - mixed schedule ahead'
        }
    
    def print_fantasy_rankings(self, top_n: int = 15):
        """Print fantasy rankings in a formatted table"""
        rankings = self.get_fantasy_rankings(top_n)
        
        print(f"\n{'='*80}")
        print(f"FANTASY FOOTBALL QB RANKINGS (Top {top_n})")
        print(f"{'='*80}")
        print(f"{'Rank':<4} {'Name':<20} {'Team':<4} {'Avg Pts':<8} {'Total Pts':<10} {'Yards':<8} {'TDs':<4} {'INTs':<4}")
        print(f"{'-'*80}")
        
        for qb in rankings:
            print(f"{qb['rank']:<4} {qb['name']:<20} {qb['team']:<4} {qb['fantasy_points_avg']:<8} "
                  f"{qb['fantasy_points_total']:<10} {qb['yards']:<8} {qb['touchdowns']:<4} {qb['interceptions']:<4}")
        
        print(f"{'='*80}")
    
    def print_start_sit_recommendations(self):
        """Print start/sit recommendations"""
        recommendations = self.get_start_sit_recommendations()
        
        print(f"\n{'='*60}")
        print("FANTASY FOOTBALL START/SIT RECOMMENDATIONS")
        print(f"{'='*60}")
        
        for category, qbs in recommendations.items():
            if qbs:
                print(f"\n{category.upper().replace('_', ' ')}:")
                print("-" * 40)
                for qb in qbs:
                    print(f"  {qb['name']} ({qb['team']}) - {qb['avg_points']} avg pts - {qb['reason']}")

def main():
    """Example usage of the FantasyFootballAnalyzer"""
    print("Fantasy Football Analyzer module loaded successfully!")
    print("Use this with quarterback data from your scraper:")
    print("from src.fantasy_football import FantasyFootballAnalyzer")
    print("analyzer = FantasyFootballAnalyzer(qb_data)")
    print("analyzer.print_fantasy_rankings()")

if __name__ == "__main__":
    main()
