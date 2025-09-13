import pandas as pd
import json
from typing import Dict, List, Any
import re

def clean_data(raw_data: str) -> str:
    """Clean and normalize raw data"""
    if not raw_data:
        return ""
    
    # Remove extra whitespace
    cleaned = raw_data.strip()
    
    # Remove special characters that might interfere with parsing
    cleaned = re.sub(r'[^\w\s\.\-%]', '', cleaned)
    
    return cleaned

def format_stats(stats: Dict[str, Any]) -> Dict[str, str]:
    """Format statistics for display"""
    formatted_stats = {}
    
    for key, value in stats.items():
        if isinstance(value, float):
            if key in ['completion_pct', 'rating', 'yards_per_attempt']:
                formatted_stats[key] = f"{value:.2f}"
            else:
                formatted_stats[key] = f"{value:.0f}"
        else:
            formatted_stats[key] = str(value)
    
    return formatted_stats

def validate_qb_name(name: str) -> bool:
    """Validate if a quarterback name is reasonable"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Check for common patterns in QB names
    name_lower = name.lower()
    if any(word in name_lower for word in ['qb', 'quarterback', 'player']):
        return False
    
    return True

def normalize_qb_name(name: str) -> str:
    """Normalize quarterback name for consistent matching"""
    if not name:
        return ""
    
    # Remove common suffixes and prefixes
    name = re.sub(r'\s+(Jr\.|Sr\.|III|IV|V|VI)$', '', name)
    
    # Standardize spacing
    name = re.sub(r'\s+', ' ', name.strip())
    
    return name

def calculate_efficiency_metrics(stats: Dict[str, Any]) -> Dict[str, float]:
    """Calculate efficiency metrics for a quarterback"""
    metrics = {}
    
    attempts = stats.get('attempts', 0)
    completions = stats.get('completions', 0)
    yards = stats.get('yards', 0)
    touchdowns = stats.get('touchdowns', 0)
    interceptions = stats.get('interceptions', 0)
    
    # Completion percentage
    if attempts > 0:
        metrics['completion_percentage'] = (completions / attempts) * 100
    else:
        metrics['completion_percentage'] = 0
    
    # Yards per attempt
    if attempts > 0:
        metrics['yards_per_attempt'] = yards / attempts
    else:
        metrics['yards_per_attempt'] = 0
    
    # Touchdown to interception ratio
    if interceptions > 0:
        metrics['td_int_ratio'] = touchdowns / interceptions
    else:
        metrics['td_int_ratio'] = touchdowns if touchdowns > 0 else 0
    
    # Yards per completion
    if completions > 0:
        metrics['yards_per_completion'] = yards / completions
    else:
        metrics['yards_per_completion'] = 0
    
    return metrics

def load_qb_data(filename: str) -> Dict[str, Any]:
    """Load quarterback data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Error parsing JSON from {filename}")
        return {}

def save_qb_data(data: Dict[str, Any], filename: str):
    """Save quarterback data to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving data: {e}")

def filter_qbs_by_minimum_attempts(qb_data: Dict[str, Any], min_attempts: int = 100) -> Dict[str, Any]:
    """Filter quarterbacks by minimum passing attempts"""
    filtered_data = {}
    
    for name, stats in qb_data.items():
        if stats.get('attempts', 0) >= min_attempts:
            filtered_data[name] = stats
    
    return filtered_data

def get_qb_rankings(qb_data: Dict[str, Any], stat: str = 'yards') -> List[tuple]:
    """Get quarterback rankings by a specific stat"""
    if not qb_data:
        return []
    
    # Sort by the specified stat
    sorted_qbs = sorted(
        qb_data.items(),
        key=lambda x: x[1].get(stat, 0),
        reverse=True
    )
    
    return sorted_qbs

def create_comparison_table(qb_names: List[str], qb_data: Dict[str, Any], 
                          stats: List[str] = None) -> pd.DataFrame:
    """Create a comparison table for multiple quarterbacks"""
    if stats is None:
        stats = ['yards', 'touchdowns', 'interceptions', 'completion_pct', 'rating']
    
    comparison_data = []
    
    for qb_name in qb_names:
        qb_stats = qb_data.get(qb_name)
        if qb_stats:
            row = {'quarterback': qb_name, 'team': qb_stats.get('team', 'N/A')}
            for stat in stats:
                row[stat] = qb_stats.get(stat, 0)
            comparison_data.append(row)
    
    return pd.DataFrame(comparison_data)

def print_qb_summary(qb_name: str, qb_data: Dict[str, Any]):
    """Print a formatted summary for a quarterback"""
    qb_stats = qb_data.get(qb_name)
    if not qb_stats:
        print(f"Quarterback '{qb_name}' not found in data")
        return
    
    print(f"\n{'='*50}")
    print(f"QUARTERBACK SUMMARY: {qb_name}")
    print(f"{'='*50}")
    print(f"Team: {qb_stats.get('team', 'N/A')}")
    print(f"Games Played: {qb_stats.get('games_played', 0)}")
    print(f"Passing Yards: {qb_stats.get('yards', 0):,}")
    print(f"Touchdowns: {qb_stats.get('touchdowns', 0)}")
    print(f"Interceptions: {qb_stats.get('interceptions', 0)}")
    print(f"Completion %: {qb_stats.get('completion_pct', 0):.1f}%")
    print(f"Passer Rating: {qb_stats.get('rating', 0):.1f}")
    print(f"Yards per Attempt: {qb_stats.get('yards_per_attempt', 0):.1f}")
    print(f"{'='*50}")

def main():
    """Example usage of utility functions"""
    print("Utility functions for ESPN QB Scraper")
    print("Available functions:")
    print("- clean_data(): Clean raw data")
    print("- format_stats(): Format statistics for display")
    print("- validate_qb_name(): Validate quarterback names")
    print("- normalize_qb_name(): Normalize quarterback names")
    print("- calculate_efficiency_metrics(): Calculate efficiency metrics")
    print("- load_qb_data(): Load data from JSON file")
    print("- save_qb_data(): Save data to JSON file")
    print("- filter_qbs_by_minimum_attempts(): Filter QBs by minimum attempts")
    print("- get_qb_rankings(): Get QB rankings by stat")
    print("- create_comparison_table(): Create comparison table")
    print("- print_qb_summary(): Print QB summary")

if __name__ == "__main__":
    main()