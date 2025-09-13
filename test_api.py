#!/usr/bin/env python3
"""
Test ESPN API to see what data we can access
"""

import requests
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_espn_api():
    """Test various ESPN API endpoints"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    base_url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    # Test 1: Teams endpoint
    print("Testing teams endpoint...")
    try:
        response = session.get(f"{base_url}/teams", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Teams found: {len(data.get('sports', []))}")
            
            # Look for teams
            for sport in data.get('sports', []):
                for league in sport.get('leagues', []):
                    teams = league.get('teams', [])
                    print(f"Found {len(teams)} teams in {league.get('name', 'Unknown')}")
                    
                    # Show first few teams
                    for i, team in enumerate(teams[:3]):
                        team_info = team.get('team', {})
                        print(f"  {i+1}. {team_info.get('displayName', 'Unknown')} (ID: {team_info.get('id', 'N/A')})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing teams: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: Try to get a specific team's roster
    print("Testing team roster endpoint...")
    try:
        # Try with Kansas City Chiefs (ID: 10)
        response = session.get(f"{base_url}/teams/10/roster", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            athletes = data.get('athletes', [])
            print(f"Athletes found: {len(athletes)}")
            
            # Look for quarterbacks
            qbs = []
            for athlete in athletes:
                player_info = athlete.get('athlete', {})
                position = player_info.get('position', {})
                
                if position.get('abbreviation') == 'QB':
                    qbs.append(player_info.get('displayName', 'Unknown'))
            
            print(f"Quarterbacks found: {len(qbs)}")
            for qb in qbs:
                print(f"  - {qb}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing roster: {e}")
    
    print("\n" + "="*50)
    
    # Test 3: Try to get player stats
    print("Testing player stats endpoint...")
    try:
        # Try with Patrick Mahomes (ID: 3139477)
        response = session.get(f"{base_url}/athletes/3139477/statistics", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Stats data structure:")
            print(json.dumps(data, indent=2)[:1000] + "...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing stats: {e}")
    
    print("\n" + "="*50)
    
    # Test 4: Try alternative endpoints
    print("Testing alternative endpoints...")
    
    alternative_urls = [
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/statistics",
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/athletes",
        "https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings"
    ]
    
    for url in alternative_urls:
        try:
            print(f"\nTesting: {url}")
            response = session.get(url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response keys: {list(data.keys())}")
            else:
                print(f"Error: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_espn_api()
