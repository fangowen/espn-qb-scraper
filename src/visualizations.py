import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import os

class QBVisualizer:
    def __init__(self, qb_data: Dict[str, Dict]):
        self.qb_data = qb_data
        self.df = pd.DataFrame.from_dict(qb_data, orient='index')
        
        # Set style for better-looking charts
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create output directory for charts
        os.makedirs('charts', exist_ok=True)
    
    def plot_top_qbs_bar(self, stat: str = 'yards', top_n: int = 10, save: bool = True):
        """Create horizontal bar chart of top quarterbacks by a specific stat"""
        top_qbs = self.df.nlargest(top_n, stat)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(top_qbs.index, top_qbs[stat], color='skyblue', edgecolor='navy', alpha=0.8)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + width*0.01, bar.get_y() + bar.get_height()/2, 
                    f'{width:,.0f}', ha='left', va='center', fontweight='bold')
        
        plt.title(f'Top {top_n} Quarterbacks by {stat.replace("_", " ").title()}', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(stat.replace("_", " ").title(), fontsize=12)
        plt.ylabel('Quarterback', fontsize=12)
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        if save:
            plt.savefig(f'charts/top_qbs_{stat}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_scatter_comparison(self, x_stat: str = 'yards', y_stat: str = 'touchdowns', 
                               save: bool = True):
        """Create scatter plot comparing two quarterback statistics"""
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        scatter = plt.scatter(self.df[x_stat], self.df[y_stat], 
                            s=100, alpha=0.7, c=self.df['rating'], 
                            cmap='viridis', edgecolors='black', linewidth=1)
        
        # Add quarterback names as annotations
        for idx, row in self.df.iterrows():
            plt.annotate(idx, (row[x_stat], row[y_stat]), 
                        xytext=(5, 5), textcoords='offset points', 
                        fontsize=9, fontweight='bold', alpha=0.8)
        
        # Add colorbar for passer rating
        cbar = plt.colorbar(scatter)
        cbar.set_label('Passer Rating', fontsize=12)
        
        plt.xlabel(x_stat.replace("_", " ").title(), fontsize=12)
        plt.ylabel(y_stat.replace("_", " ").title(), fontsize=12)
        plt.title(f'{x_stat.replace("_", " ").title()} vs {y_stat.replace("_", " ").title()}\n(Color = Passer Rating)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'charts/scatter_{x_stat}_vs_{y_stat}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_radar_comparison(self, qb1_name: str, qb2_name: str, save: bool = True):
        """Create radar chart comparing two quarterbacks across multiple stats"""
        # Get quarterback data
        qb1_data = self.qb_data.get(qb1_name)
        qb2_data = self.qb_data.get(qb2_name)
        
        if not qb1_data or not qb2_data:
            print(f"One or both quarterbacks not found: {qb1_name}, {qb2_name}")
            return
        
        # Stats to compare (normalized to 0-100 scale)
        stats = ['completion_pct', 'yards_per_attempt', 'rating', 'touchdowns', 'yards']
        stat_labels = ['Completion %', 'Yards/Attempt', 'Passer Rating', 'Touchdowns', 'Passing Yards']
        
        # Normalize data (simple min-max scaling for demo)
        qb1_values = []
        qb2_values = []
        
        for stat in stats:
            if stat in ['completion_pct', 'rating']:
                # These are already in good ranges
                qb1_values.append(qb1_data[stat])
                qb2_values.append(qb2_data[stat])
            else:
                # Normalize other stats
                max_val = self.df[stat].max()
                qb1_values.append((qb1_data[stat] / max_val) * 100)
                qb2_values.append((qb2_data[stat] / max_val) * 100)
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(stats), endpoint=False).tolist()
        qb1_values += qb1_values[:1]  # Close the plot
        qb2_values += qb2_values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, qb1_values, 'o-', linewidth=2, label=qb1_name, color='red', alpha=0.8)
        ax.fill(angles, qb1_values, alpha=0.25, color='red')
        
        ax.plot(angles, qb2_values, 'o-', linewidth=2, label=qb2_name, color='blue', alpha=0.8)
        ax.fill(angles, qb2_values, alpha=0.25, color='blue')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(stat_labels)
        ax.set_ylim(0, 100)
        ax.set_title(f'{qb1_name} vs {qb2_name} Comparison', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)
        
        if save:
            plt.savefig(f'charts/radar_{qb1_name.replace(" ", "_")}_vs_{qb2_name.replace(" ", "_")}.png', 
                       dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_team_performance(self, save: bool = True):
        """Create bar chart showing average QB performance by team"""
        team_stats = self.df.groupby('team').agg({
            'yards': 'mean',
            'touchdowns': 'mean',
            'rating': 'mean'
        }).round(1)
        
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # Yards by team
        team_stats['yards'].plot(kind='bar', ax=ax1, color='skyblue', alpha=0.8)
        ax1.set_title('Average Passing Yards by Team', fontweight='bold')
        ax1.set_ylabel('Yards')
        ax1.tick_params(axis='x', rotation=45)
        
        # Touchdowns by team
        team_stats['touchdowns'].plot(kind='bar', ax=ax2, color='lightgreen', alpha=0.8)
        ax2.set_title('Average Touchdowns by Team', fontweight='bold')
        ax2.set_ylabel('Touchdowns')
        ax2.tick_params(axis='x', rotation=45)
        
        # Rating by team
        team_stats['rating'].plot(kind='bar', ax=ax3, color='lightcoral', alpha=0.8)
        ax3.set_title('Average Passer Rating by Team', fontweight='bold')
        ax3.set_ylabel('Rating')
        ax3.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save:
            plt.savefig('charts/team_performance.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_correlation_heatmap(self, save: bool = True):
        """Create correlation heatmap of quarterback statistics"""
        # Select numeric columns for correlation
        numeric_cols = ['games_played', 'completions', 'attempts', 'completion_pct', 
                       'yards', 'yards_per_attempt', 'touchdowns', 'interceptions', 'rating']
        
        correlation_matrix = self.df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        
        plt.title('Quarterback Statistics Correlation Matrix', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save:
            plt.savefig('charts/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_efficiency_analysis(self, save: bool = True):
        """Create efficiency analysis scatter plot"""
        plt.figure(figsize=(12, 8))
        
        # Calculate efficiency metrics
        self.df['td_int_ratio'] = self.df['touchdowns'] / self.df['interceptions'].replace(0, 1)
        self.df['yards_per_game'] = self.df['yards'] / self.df['games_played']
        
        # Create scatter plot
        scatter = plt.scatter(self.df['yards_per_game'], self.df['td_int_ratio'], 
                            s=100, alpha=0.7, c=self.df['rating'], 
                            cmap='viridis', edgecolors='black', linewidth=1)
        
        # Add quarterback names
        for idx, row in self.df.iterrows():
            plt.annotate(idx, (row['yards_per_game'], row['td_int_ratio']), 
                        xytext=(5, 5), textcoords='offset points', 
                        fontsize=9, fontweight='bold', alpha=0.8)
        
        # Add colorbar
        cbar = plt.colorbar(scatter)
        cbar.set_label('Passer Rating', fontsize=12)
        
        plt.xlabel('Yards per Game', fontsize=12)
        plt.ylabel('Touchdown to Interception Ratio', fontsize=12)
        plt.title('QB Efficiency Analysis\n(Yards per Game vs TD/INT Ratio)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save:
            plt.savefig('charts/efficiency_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_all_charts(self):
        """Generate all visualization charts"""
        print("Generating quarterback visualization charts...")
        
        # Top QBs by different stats
        self.plot_top_qbs_bar('yards', 10)
        self.plot_top_qbs_bar('touchdowns', 10)
        self.plot_top_qbs_bar('rating', 10)
        
        # Scatter plots
        self.plot_scatter_comparison('yards', 'touchdowns')
        self.plot_scatter_comparison('completion_pct', 'rating')
        self.plot_scatter_comparison('yards_per_attempt', 'interceptions')
        
        # Team performance
        self.plot_team_performance()
        
        # Correlation analysis
        self.plot_correlation_heatmap()
        
        # Efficiency analysis
        self.plot_efficiency_analysis()
        
        print("All charts generated and saved in 'charts' directory!")

def main():
    """Example usage of the QBVisualizer"""
    # This would typically be used with data from the scraper
    print("QBVisualizer module loaded successfully!")
    print("Use this with quarterback data from your scraper:")
    print("from src.visualizations import QBVisualizer")
    print("viz = QBVisualizer(qb_data)")
    print("viz.generate_all_charts()")

if __name__ == "__main__":
    main()
