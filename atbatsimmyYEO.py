"""
atbatsimmyYeo.py - Oberlin Baseball At-Bat Simulator
Simulates individual at-bats between any Oberlin batter and pitcher
"""

import json
import random
import numpy as np
from typing import Dict, List, Tuple, Optional


class OberlinAtBatSimulator:
    def __init__(self):
        """Initialize the Oberlin at-bat simulator"""
        self.batters = self.load_batters()
        self.pitchers = self.load_pitchers()
        print(f"✅ Loaded {len(self.batters)} batters and {len(self.pitchers)} pitchers")

    def load_batters(self) -> Dict:
        """Load batter data from JSON"""
        try:
            with open('oberlin_baseball_data/batters.json', 'r') as f:
                batters_list = json.load(f)
            # Convert to dict with player_id as key
            return {b['player_id']: b for b in batters_list}
        except FileNotFoundError:
            print("❌ Error: oberlin_baseball_data/batters.json not found!")
            return {}

    def load_pitchers(self) -> Dict:
        """Load pitcher data from JSON"""
        try:
            with open('oberlin_baseball_data/pitchers.json', 'r') as f:
                pitchers_list = json.load(f)
            # Convert to dict with player_id as key
            return {p['player_id']: p for p in pitchers_list}
        except FileNotFoundError:
            print("❌ Error: oberlin_baseball_data/pitchers.json not found!")
            return {}

    def find_player(self, identifier: str, player_dict: Dict, player_type: str) -> Optional[Dict]:
        """Find a player by ID, name, or jersey number"""
        identifier = identifier.strip().upper()

        # Try exact player_id match first
        for pid, player in player_dict.items():
            if pid.upper() == identifier:
                return player

        # Try by name (partial match)
        for pid, player in player_dict.items():
            if identifier in player['name'].upper():
                return player

        # Try by jersey number and year
        if '_' in identifier:  # Format: JERSEY_YEAR
            parts = identifier.split('_')
            if len(parts) == 2:
                jersey, year = parts
                for pid, player in player_dict.items():
                    if str(player.get('jersey')) == jersey and str(player.get('year')) == year:
                        return player

        # Try by jersey number only (return most recent)
        matching = []
        for pid, player in player_dict.items():
            if str(player.get('jersey')) == identifier:
                matching.append(player)
        if matching:
            # Return most recent year
            return max(matching, key=lambda x: x.get('year', 0))

        return None

    def get_outcomes(self, batter: Dict, pitcher: Dict) -> List[Tuple[str, float]]:
        """Get outcome probabilities for a batter-pitcher matchup"""
        # For simplicity, average the batter and pitcher outcome probabilities
        outcomes = []
        outcome_types = ['1B%', '2B%', '3B%', 'HR%', 'BB%', 'K%', 'HBP%', 'FO%']

        for outcome in outcome_types:
            # Average batter and pitcher tendencies
            batter_prob = batter.get(outcome, 0.125)  # Default to 1/8 if missing
            pitcher_prob = pitcher.get(outcome, 0.125)
            avg_prob = (batter_prob + pitcher_prob) / 2

            # Convert outcome name
            outcome_name = outcome.replace('%', '')
            outcomes.append((outcome_name, avg_prob))

        # Normalize probabilities
        total = sum(prob for _, prob in outcomes)
        if total > 0:
            outcomes = [(name, prob / total) for name, prob in outcomes]

        return outcomes

    def simulate_at_bat(self, batter: Dict, pitcher: Dict) -> str:
        """Simulate a single at-bat"""
        outcomes = self.get_outcomes(batter, pitcher)

        # Create probability distribution
        outcome_names = [name for name, _ in outcomes]
        probabilities = [prob for _, prob in outcomes]

        # Simulate the outcome
        result = np.random.choice(outcome_names, p=probabilities)

        return result

    def format_result(self, result: str) -> str:
        """Format the result for display"""
        result_map = {
            '1B': 'Single',
            '2B': 'Double',
            '3B': 'Triple',
            'HR': 'Home Run',
            'BB': 'Walk',
            'K': 'Strikeout',
            'HBP': 'Hit by Pitch',
            'FO': 'Fielded Out'
        }
        return result_map.get(result, result)

    def simulate_multiple_at_bats(self, batter: Dict, pitcher: Dict, n: int = 1000) -> Dict:
        """Simulate multiple at-bats and return statistics"""
        results = []
        for _ in range(n):
            result = self.simulate_at_bat(batter, pitcher)
            results.append(result)

        # Calculate statistics
        stats = {}
        outcomes = ['1B', '2B', '3B', 'HR', 'BB', 'K', 'HBP', 'FO']
        for outcome in outcomes:
            count = results.count(outcome)
            stats[outcome] = {
                'count': count,
                'pct': count / n
            }

        # Calculate batting average and other stats
        hits = sum(results.count(x) for x in ['1B', '2B', '3B', 'HR'])
        at_bats = n - results.count('BB') - results.count('HBP')

        stats['summary'] = {
            'AVG': hits / at_bats if at_bats > 0 else 0,
            'OBP': (hits + results.count('BB') + results.count('HBP')) / n,
            'SLG': self.calculate_slg(results, at_bats),
            'total_sims': n
        }

        return stats

    def calculate_slg(self, results: List[str], at_bats: int) -> float:
        """Calculate slugging percentage"""
        if at_bats == 0:
            return 0
        total_bases = (results.count('1B') +
                       results.count('2B') * 2 +
                       results.count('3B') * 3 +
                       results.count('HR') * 4)
        return total_bases / at_bats

    def print_matchup_info(self, batter: Dict, pitcher: Dict):
        """Print information about the matchup"""
        print("\n" + "=" * 60)
        print(f"MATCHUP: {batter['name']} (#{batter['jersey']}) vs {pitcher['name']} (#{pitcher['jersey']})")
        print("=" * 60)
        print(f"\nBatter: {batter['name']} - {batter.get('year', 'Unknown')} Season")
        print(f"  AVG: {batter.get('avg', 'N/A'):.3f} | OPS: {batter.get('ops', 'N/A'):.3f}")
        print(f"  PA: {batter.get('pa', 'N/A')} | HR: {batter.get('hr', 'N/A')} | RBI: {batter.get('rbi', 'N/A')}")

        print(f"\nPitcher: {pitcher['name']} - {pitcher.get('year', 'Unknown')} Season")
        print(f"  ERA: {pitcher.get('era', 'N/A'):.2f} | WHIP: {pitcher.get('whip', 'N/A'):.2f}")
        print(
            f"  W-L: {pitcher.get('w', 0)}-{pitcher.get('l', 0)} | K: {pitcher.get('so', 'N/A')} | IP: {pitcher.get('ip', 'N/A')}")

    def print_simulation_results(self, stats: Dict):
        """Print simulation results"""
        print("\nSimulation Results:")
        print("-" * 40)
        print(f"{'Outcome':<15} {'Count':<10} {'Percentage':<10}")
        print("-" * 40)

        for outcome in ['1B', '2B', '3B', 'HR', 'BB', 'K', 'HBP', 'FO']:
            result = stats[outcome]
            formatted = self.format_result(outcome)
            print(f"{formatted:<15} {result['count']:<10} {result['pct'] * 100:<10.1f}%")

        print("-" * 40)
        summary = stats['summary']
        print(f"\nBatting Stats ({summary['total_sims']} simulations):")
        print(f"  AVG: {summary['AVG']:.3f}")
        print(f"  OBP: {summary['OBP']:.3f}")
        print(f"  SLG: {summary['SLG']:.3f}")
        print(f"  OPS: {summary['OBP'] + summary['SLG']:.3f}")

    def list_players(self, year: Optional[int] = None):
        """List available players"""
        print("\n" + "=" * 60)
        print("AVAILABLE OBERLIN PLAYERS")
        print("=" * 60)

        # Filter by year if specified
        batters = list(self.batters.values())
        pitchers = list(self.pitchers.values())

        if year:
            batters = [b for b in batters if b.get('year') == year]
            pitchers = [p for p in pitchers if p.get('year') == year]

        # Sort by jersey number
        batters.sort(key=lambda x: int(x.get('jersey', 0)))
        pitchers.sort(key=lambda x: int(x.get('jersey', 0)))

        print(f"\nBatters ({len(batters)}):")
        print("-" * 40)
        for b in batters:
            print(f"  #{b['jersey']:<3} {b['name']:<20} ({b['year']}) - AVG: {b.get('avg', 0):.3f}")

        print(f"\nPitchers ({len(pitchers)}):")
        print("-" * 40)
        for p in pitchers:
            print(f"  #{p['jersey']:<3} {p['name']:<20} ({p['year']}) - ERA: {p.get('era', 0):.2f}")


def main():
    """Main function to run the simulator"""
    print("\n" + "=" * 60)
    print("OBERLIN BASEBALL AT-BAT SIMULATOR")
    print("=" * 60)

    sim = OberlinAtBatSimulator()

    while True:
        print("\nOptions:")
        print("1. Simulate at-bat")
        print("2. List players")
        print("3. Quit")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == '1':
            # Get batter
            print("\nEnter batter (name, jersey #, or jersey#_year):")
            batter_id = input("Batter: ").strip()
            batter = sim.find_player(batter_id, sim.batters, "batter")

            if not batter:
                print(f"❌ Batter '{batter_id}' not found!")
                continue

            # Get pitcher
            print("\nEnter pitcher (name, jersey #, or jersey#_year):")
            pitcher_id = input("Pitcher: ").strip()
            pitcher = sim.find_player(pitcher_id, sim.pitchers, "pitcher")

            if not pitcher:
                print(f"❌ Pitcher '{pitcher_id}' not found!")
                continue

            # Print matchup info
            sim.print_matchup_info(batter, pitcher)

            # Get number of simulations
            n_sims = input("\nNumber of simulations (default 1000): ").strip()
            n_sims = int(n_sims) if n_sims.isdigit() else 1000

            # Run simulation
            print(f"\nSimulating {n_sims} at-bats...")
            stats = sim.simulate_multiple_at_bats(batter, pitcher, n_sims)
            sim.print_simulation_results(stats)

            # Single at-bat simulation
            single = input("\nSimulate a single at-bat? (y/n): ").strip().lower()
            if single == 'y':
                result = sim.simulate_at_bat(batter, pitcher)
                print(f"\n🎯 Result: {sim.format_result(result)}!")

        elif choice == '2':
            year = input("\nFilter by year (2023/2024/2025) or press Enter for all: ").strip()
            year = int(year) if year.isdigit() else None
            sim.list_players(year)

        elif choice == '3':
            print("\nThanks for using Oberlin Baseball Simulator!")
            break

        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    main()