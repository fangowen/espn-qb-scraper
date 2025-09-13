#!/usr/bin/env python3
"""
ESPN Quarterback Scraper and Comparer
A tool to scrape quarterback statistics from ESPN and compare your favorite QBs
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hybrid_scraper import HybridQBScraper
from compare import QuarterbackComparer
from utils import print_qb_summary, create_comparison_table, filter_qbs_by_minimum_attempts
import pandas as pd

def main():
    print("🏈 ESPN Quarterback Scraper & Comparer 🏈")
    print("=" * 50)
    
    # Initialize hybrid scraper
    scraper = HybridQBScraper()
    
    # Check if database needs update
    if not os.path.exists("qb_database.db"):
        print("Database not found. Creating new database with quarterback data...")
        try:
            qb_data = scraper.update_database()
            print("✅ Database created successfully!")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            print("Using demo data...")
            qb_data = scraper.get_demo_data()
    else:
        print("✅ Database found")
        qb_data = scraper.get_all_quarterbacks()
        
        if not qb_data:
            print("Database is empty. Populating with quarterback data...")
            try:
                qb_data = scraper.update_database()
                print("✅ Database populated successfully!")
            except Exception as e:
                print(f"❌ Error populating database: {e}")
                print("Using demo data...")
                qb_data = scraper.get_demo_data()
    
    print(f"📊 Loaded {len(qb_data)} quarterbacks")
    
    # Initialize comparer
    comparer = QuarterbackComparer(qb_data)
    
    while True:
        print("QUARTERBACK ANALYSIS MENU")
        print("=" * 50)
        print("1. Compare two quarterbacks")
        print("2. View top quarterbacks by stat")
        print("3. Get quarterback summary")
        print("4. Create comparison table")
        print("5. Search quarterbacks")
        print("6. View team quarterbacks")
        print("7. Update database from ESPN")
        print("8. Export data")
        print("9. Database info")
        print("10. Generate visualizations")
        print("11. Fantasy Football Analysis")
        print("12. Exit")
        
        
        choice = input("Enter your choice (1-12): ").strip()
        
        if choice == "1":
            compare_quarterbacks(comparer)
        elif choice == "2":
            view_top_quarterbacks(comparer)
        elif choice == "3":
            get_qb_summary_menu(comparer)
        elif choice == "4":
            create_comparison_table_menu(qb_data)
        elif choice == "5":
            search_quarterbacks_menu(scraper)
        elif choice == "6":
            view_team_quarterbacks_menu(scraper)
        elif choice == "7":
            update_database_menu(scraper)
        elif choice == "8":
            export_data_menu(scraper)
        elif choice == "9":
            show_database_info(scraper)
        elif choice == "10":
            generate_visualizations_menu(scraper)
        elif choice == "11":
            fantasy_football_menu(scraper)
        elif choice == "12":
            print("Thanks for using the ESPN QB Scraper!")
            break
        else:
            print("Invalid choice. Please enter 1-12.")

def compare_quarterbacks(comparer):
    """Compare two quarterbacks head-to-head"""
    print("\n QUARTERBACK COMPARISON")
    print("-" * 30)
    
    qb1 = input("Enter first quarterback name: ").strip()
    qb2 = input("Enter second quarterback name: ").strip()
    
    if not qb1 or not qb2:
        print("Please enter both quarterback names")
        return
    
    comparer.print_comparison(qb1, qb2)

def view_top_quarterbacks(comparer):
    """View top quarterbacks by different stats"""
    print("\n🏆 TOP QUARTERBACKS")
    print("-" * 20)
    
    stats = {
        "1": ("yards", "Passing Yards"),
        "2": ("touchdowns", "Touchdowns"),
        "3": ("rating", "Passer Rating"),
        "4": ("completion_pct", "Completion Percentage"),
        "5": ("yards_per_attempt", "Yards per Attempt"),
        "6": ("interceptions", "Interceptions (Lowest)")
    }
    
    print("Select stat to rank by:")
    for key, (stat, name) in stats.items():
        print(f"{key}. {name}")
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice in stats:
        stat, name = stats[choice]
        limit = input("How many quarterbacks to show? (default 10): ").strip()
        limit = int(limit) if limit.isdigit() else 10
        
        comparer.print_top_qbs(stat, limit)
    else:
        print("❌ Invalid choice")

def get_qb_summary_menu(comparer):
    """Get detailed summary for a quarterback"""
    print("\n📋 QUARTERBACK SUMMARY")
    print("-" * 25)
    
    qb_name = input("Enter quarterback name: ").strip()
    
    if not qb_name:
        print("❌ Please enter a quarterback name")
        return
    
    summary = comparer.get_qb_summary(qb_name)
    
    if "error" in summary:
        print(f"❌ {summary['error']}")
        return
    
    print(f"\n{'='*50}")
    print(f"📊 {summary['name'].upper()} SUMMARY")
    print(f"{'='*50}")
    print(f"Team: {summary['team']}")
    print(f"Games Played: {summary['games_played']}")
    print(f"Passing Yards: {summary['passing_yards']:,}")
    print(f"Touchdowns: {summary['touchdowns']}")
    print(f"Interceptions: {summary['interceptions']}")
    print(f"Completion %: {summary['completion_percentage']:.1f}%")
    print(f"Passer Rating: {summary['passer_rating']:.1f}")
    print(f"Yards per Attempt: {summary['yards_per_attempt']:.1f}")
    print(f"TD/INT Ratio: {summary['td_to_int_ratio']:.2f}")
    print(f"{'='*50}")

def create_comparison_table_menu(qb_data):
    """Create a comparison table for multiple quarterbacks"""
    print("\n📊 COMPARISON TABLE")
    print("-" * 20)
    
    qb_names_input = input("Enter quarterback names (comma-separated): ").strip()
    
    if not qb_names_input:
        print("❌ Please enter quarterback names")
        return
    
    qb_names = [name.strip() for name in qb_names_input.split(",")]
    
    # Filter data to only include requested QBs
    filtered_data = {}
    for name in qb_names:
        for qb_name, stats in qb_data.items():
            if name.lower() in qb_name.lower():
                filtered_data[qb_name] = stats
                break
    
    if not filtered_data:
        print("❌ No quarterbacks found")
        return
    
    # Create comparison table
    df = create_comparison_table(list(filtered_data.keys()), qb_data)
    
    if not df.empty:
        print("\n" + "="*80)
        print("📊 QUARTERBACK COMPARISON TABLE")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80)
        
        # Save to CSV
        save_choice = input("\nSave to CSV? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = "qb_comparison.csv"
            df.to_csv(filename, index=False)
            print(f"✅ Comparison table saved to {filename}")
    else:
        print("❌ No data to display")

def search_quarterbacks_menu(scraper):
    """Search for quarterbacks by name"""
    print("\n🔍 SEARCH QUARTERBACKS")
    print("-" * 25)
    
    search_term = input("Enter search term: ").strip()
    
    if not search_term:
        print("❌ Please enter a search term")
        return
    
    qb_data = scraper.get_all_quarterbacks()
    results = []
    
    for name, stats in qb_data.items():
        if search_term.lower() in name.lower():
            results.append({
                'name': name,
                'team': stats['team'],
                'yards': stats['yards'],
                'touchdowns': stats['touchdowns'],
                'interceptions': stats['interceptions']
            })
    
    if results:
        print(f"\nFound {len(results)} quarterbacks:")
        print("-" * 60)
        for qb in results:
            print(f"{qb['name']} ({qb['team']}) - {qb['yards']} yards, {qb['touchdowns']} TD, {qb['interceptions']} INT")
    else:
        print("❌ No quarterbacks found")

def view_team_quarterbacks_menu(scraper):
    """View quarterbacks for a specific team"""
    print("\n🏈 TEAM QUARTERBACKS")
    print("-" * 25)
    
    team = input("Enter team abbreviation (e.g., KC, BUF, NE): ").strip().upper()
    
    if not team:
        print("❌ Please enter a team abbreviation")
        return
    
    qb_data = scraper.get_all_quarterbacks()
    team_qbs = []
    
    for name, stats in qb_data.items():
        if stats['team'] == team:
            team_qbs.append({
                'name': name,
                'yards': stats['yards'],
                'touchdowns': stats['touchdowns'],
                'rating': stats['rating']
            })
    
    if team_qbs:
        print(f"\nQuarterbacks for {team}:")
        print("-" * 50)
        for qb in team_qbs:
            print(f"{qb['name']} - {qb['yards']} yards, {qb['touchdowns']} TD, {qb['rating']:.1f} rating")
    else:
        print(f"❌ No quarterbacks found for {team}")

def update_database_menu(scraper):
    """Update the database with fresh data"""
    print("\n🔄 UPDATE DATABASE")
    print("-" * 20)
    
    print("Update options:")
    print("1. Try to fetch from ESPN (API/Web)")
    print("2. Force demo data")
    
    choice = input("Enter choice (1-2): ").strip()
    
    try:
        if choice == "1":
            qb_data = scraper.update_database(force_demo=False)
        elif choice == "2":
            qb_data = scraper.update_database(force_demo=True)
        else:
            print("❌ Invalid choice")
            return
        
        print(f"✅ Database updated with {len(qb_data)} quarterbacks!")
    except Exception as e:
        print(f"❌ Error updating database: {e}")

def export_data_menu(scraper):
    """Export data in various formats"""
    print("\n📤 EXPORT DATA")
    print("-" * 15)
    
    print("Export formats:")
    print("1. CSV")
    print("2. JSON")
    
    choice = input("Select format (1-2): ").strip()
    
    try:
        if choice == "1":
            scraper.export_to_csv()
        elif choice == "2":
            scraper.export_to_json()
        else:
            print("❌ Invalid choice")
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def show_database_info(scraper):
    """Show database information"""
    print("\n📊 DATABASE INFORMATION")
    print("-" * 25)
    
    try:
        qb_data = scraper.get_all_quarterbacks()
        
        print(f"Quarterbacks: {len(qb_data)}")
        
        # Get some stats
        if qb_data:
            total_yards = sum(stats['yards'] for stats in qb_data.values())
            avg_yards = total_yards / len(qb_data)
            print(f"Total passing yards: {total_yards:,}")
            print(f"Average yards per QB: {avg_yards:,.0f}")
            
            # Show teams represented
            teams = set(stats['team'] for stats in qb_data.values())
            print(f"Teams represented: {len(teams)}")
            print(f"Teams: {', '.join(sorted(teams))}")
        
        # Check database file
        if os.path.exists("qb_database.db"):
            file_size = os.path.getsize("qb_database.db")
            print(f"Database file size: {file_size:,} bytes")
        else:
            print("Database file: Not found")
            
    except Exception as e:
        print(f"❌ Error getting database info: {e}")

def generate_visualizations_menu(scraper):
    """Generate visualization charts"""
    print("\n📊 GENERATE VISUALIZATIONS")
    print("-" * 30)
    
    try:
        from src.visualizations import QBVisualizer
        
        qb_data = scraper.get_all_quarterbacks()
        
        if not qb_data:
            print("❌ No quarterback data available")
            return
        
        print("Visualization options:")
        print("1. Generate all charts")
        print("2. Top QBs bar chart")
        print("3. Scatter plot comparison")
        print("4. Radar chart comparison")
        print("5. Team performance charts")
        print("6. Correlation heatmap")
        print("7. Efficiency analysis")
        
        choice = input("Enter choice (1-7): ").strip()
        
        viz = QBVisualizer(qb_data)
        
        if choice == "1":
            viz.generate_all_charts()
        elif choice == "2":
            stat = input("Enter stat (yards/touchdowns/rating): ").strip() or "yards"
            viz.plot_top_qbs_bar(stat, 10)
        elif choice == "3":
            x_stat = input("Enter X-axis stat (default: yards): ").strip() or "yards"
            y_stat = input("Enter Y-axis stat (default: touchdowns): ").strip() or "touchdowns"
            viz.plot_scatter_comparison(x_stat, y_stat)
        elif choice == "4":
            qb1 = input("Enter first QB name: ").strip()
            qb2 = input("Enter second QB name: ").strip()
            if qb1 and qb2:
                viz.plot_radar_comparison(qb1, qb2)
            else:
                print("❌ Please enter both quarterback names")
        elif choice == "5":
            viz.plot_team_performance()
        elif choice == "6":
            viz.plot_correlation_heatmap()
        elif choice == "7":
            viz.plot_efficiency_analysis()
        else:
            print("❌ Invalid choice")
            
        #print("✅ Charts saved in 'charts' directory!")
        
    except ImportError:
        print("❌ Visualization module not found. Please ensure matplotlib and seaborn are installed.")
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")

def fantasy_football_menu(scraper):
    """Fantasy football analysis menu"""
    print("\n🏈 FANTASY FOOTBALL ANALYSIS")
    print("-" * 30)
    
    try:
        from src.fantasy_football import FantasyFootballAnalyzer
        
        qb_data = scraper.get_all_quarterbacks()
        
        if not qb_data:
            print("❌ No quarterback data available")
            return
        
        analyzer = FantasyFootballAnalyzer(qb_data)
        
        print("Fantasy Football options:")
        print("1. View fantasy rankings")
        print("2. Start/Sit recommendations")
        print("3. Weekly projections")
        print("4. Trade value analysis")
        print("5. Waiver wire targets")
        print("6. Strength of schedule")
        
        choice = input("Enter choice (1-6): ").strip()
        
        if choice == "1":
            top_n = input("How many QBs to show? (default 15): ").strip()
            top_n = int(top_n) if top_n.isdigit() else 15
            analyzer.print_fantasy_rankings(top_n)
        elif choice == "2":
            analyzer.print_start_sit_recommendations()
        elif choice == "3":
            projections = analyzer.get_weekly_projections()
            print("\n" + "="*80)
            print("WEEKLY FANTASY PROJECTIONS")
            print("="*80)
            print(f"{'Name':<20} {'Team':<4} {'Proj Yards':<10} {'Proj TDs':<8} {'Proj INTs':<8} {'Proj Pts':<8} {'Confidence':<10}")
            print("-"*80)
            for name, proj in projections.items():
                print(f"{name:<20} {proj['team']:<4} {proj['projected_yards']:<10} {proj['projected_touchdowns']:<8} "
                      f"{proj['projected_interceptions']:<8} {proj['projected_points']:<8} {proj['confidence']:<10}")
            print("="*80)
        elif choice == "4":
            qb1 = input("Enter first QB name: ").strip()
            qb2 = input("Enter second QB name: ").strip()
            if qb1 and qb2:
                trade_analysis = analyzer.analyze_trade_value(qb1, qb2)
                if trade_analysis:
                    print(f"\n{'='*60}")
                    print("TRADE VALUE ANALYSIS")
                    print(f"{'='*60}")
                    print(f"{qb1} ({trade_analysis['qb1']['team']}): {trade_analysis['qb1']['avg_points']} avg pts")
                    print(f"{qb2} ({trade_analysis['qb2']['team']}): {trade_analysis['qb2']['avg_points']} avg pts")
                    print(f"Point difference: {trade_analysis['point_difference']}")
                    print(f"Recommendation: {trade_analysis['recommendation']}")
                    print(f"{'='*60}")
                else:
                    print("❌ One or both quarterbacks not found")
            else:
                print("❌ Please enter both quarterback names")
        elif choice == "5":
            waiver_targets = analyzer.get_waiver_wire_targets()
            if waiver_targets:
                print("\n" + "="*70)
                print("WAIVER WIRE TARGETS")
                print("="*70)
                print(f"{'Name':<20} {'Team':<4} {'Avg Pts':<8} {'Ownership':<10} {'Priority':<8} {'Reason':<20}")
                print("-"*70)
                for target in waiver_targets:
                    print(f"{target['name']:<20} {target['team']:<4} {target['avg_points']:<8} "
                          f"{target['ownership']}%{'':<6} {target['priority']:<8} {target['reason']:<20}")
                print("="*70)
            else:
                print("❌ No waiver wire targets found")
        elif choice == "6":
            qb_name = input("Enter QB name: ").strip()
            if qb_name:
                sos = analyzer.get_strength_of_schedule(qb_name)
                print(f"\n{'='*50}")
                print(f"STRENGTH OF SCHEDULE: {qb_name}")
                print(f"{'='*50}")
                print(f"Remaining weeks: {sos['remaining_weeks']}")
                print(f"Difficulty: {sos['difficulty']}")
                print(f"Favorable matchups: {sos['favorable_matchups']}")
                print(f"Tough matchups: {sos['tough_matchups']}")
                print(f"Neutral matchups: {sos['neutral_matchups']}")
                print(f"Recommendation: {sos['recommendation']}")
                print(f"{'='*50}")
            else:
                print("❌ Please enter a quarterback name")
        else:
            print("❌ Invalid choice")
            
    except ImportError:
        print("❌ Fantasy Football module not found.")
    except Exception as e:
        print(f"❌ Error in fantasy football analysis: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your internet connection and try again.")
