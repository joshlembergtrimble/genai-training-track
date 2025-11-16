"""
ESPN Fantasy Football API Client

This module provides functions to interact with the ESPN Fantasy Football API
to retrieve league data, team information, matchups, and player statistics.
"""

import httpx
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fantasy")


# Global configuration variables
BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons"
LEAGUE_ID = 747820582
YEAR = 2025
ESPN_S2 = "AEAU5wYJjkLyrnaKAt30DqQPWN4eNQ1WObzLBWVXtRcv31njomQ9q9KEDNNWk%2FT8PEXV%2B%2FIRYpR1GARjOPHEuesnZdsH0qm6V7hERPx%2FV4PoMllTg7k6nJXyVmrvsNNLyYsvVHJWawDmcp3AvoQBOyEDBKq0xtI2C4CNVTQqVq87dYzHTdeNJwastHLayMS0ba0jZQNFVeka79aafLEJ62rLzFEfxC6b58GYiXPBR9%2F9RQukaiE6ewAI2bAhaKgNDTYr9YDVz4%2BeRrh3k42t3mRr"
SWID = "{1ABB0930-509F-4DBF-ABE8-7B0BF58E6132}"


def get_endpoint() -> str:
    """Get the API endpoint URL."""
    return f"{BASE_URL}/{YEAR}/segments/0/leagues/{LEAGUE_ID}"


def get_cookies() -> Dict[str, str]:
    """Build cookies dictionary for authenticated requests."""
    if ESPN_S2 and SWID:
        return {"espn_s2": ESPN_S2, "swid": SWID}
    return {}


def make_request(params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make a request to the ESPN Fantasy API.
    
    Args:
        params: Optional query parameters
        
    Returns:
        JSON response as a dictionary
        
    Raises:
        httpx.HTTPError: If the request fails
    """
    cookies = get_cookies()
    endpoint = get_endpoint()
    
    try:
        response = httpx.get(
            endpoint,
            params=params,
            cookies=cookies,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise

@mcp.tool()
def get_league_info() -> Dict[str, Any]:
    """
    Get basic ESPN league information.
    
    Returns:
        Dictionary containing league settings and metadata
    """
    params = {
        "view": "mSettings"
    }
    return make_request(params)

@mcp.tool()
def get_teams() -> List[Dict[str, Any]]:
    """
    Get all teams in the ESPN league.
    
    Returns:
        List of team dictionaries with roster and owner information
    """
    params = {
        "view": "mTeam"
    }
    data = make_request(params)
    return data.get("teams", [])

@mcp.tool()
def get_rosters(team_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get detailed roster information for all teams or a specific team in ESPN league.
    
    Args:
        team_id: Optional specific team ID to get roster for
    
    Returns:
        Dictionary containing roster data
    """
    params = {
        "view": "mRoster"
    }
    if team_id:
        params["rosterForTeamId"] = team_id
    return make_request(params)

@mcp.tool()
def get_matchups(week: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get matchup information for a specific week in ESPN league.
    
    Args:
        week: The week number (if None, returns current week)
        
    Returns:
        List of matchup dictionaries
    """
    params = {
        "view": "mMatchup"
    }
    if week:
        params["scoringPeriodId"] = week
        
    data = make_request(params)
    return data.get("schedule", [])

@mcp.tool()
def get_standings() -> List[Dict[str, Any]]:
    """
    Get current ESPN league standings.
    
    Returns:
        List of teams sorted by standings
    """
    params = {
        "view": "mTeam"  # Changed from mStandings to get full team data including names and records
    }
    data = make_request(params)
    teams = data.get("teams", [])
    
    # Sort by wins, then by points
    sorted_teams = sorted(
        teams,
        key=lambda x: (x.get("record", {}).get("overall", {}).get("wins", 0),
                      x.get("points", 0)),
        reverse=True
    )
    return sorted_teams

@mcp.tool()
def get_player_stats(week: Optional[int] = None) -> Dict[str, Any]:
    """
    Get player statistics for a specific week from ESPN.
    
    Args:
        week: The week number (if None, returns all weeks)
        
    Returns:
        Dictionary containing player statistics
    """
    params = {
        "view": "kona_player_info"
    }
    if week:
        params["scoringPeriodId"] = week
        
    return make_request(params)

@mcp.tool()
def get_all_data(week: Optional[int] = None, team_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get comprehensive ESPN league data including teams, matchups, and settings.
    
    Args:
        week: Optional week number for matchup data
        team_id: Optional team ID for specific roster data
        
    Returns:
        Dictionary containing all league data
    """
    params = {
        "view": ["mTeam", "mRoster", "mMatchup", "mSettings", "mStandings"]
    }
    if week:
        params["scoringPeriodId"] = week
    if team_id:
        params["rosterForTeamId"] = team_id
        
    return make_request(params)

@mcp.tool()
def get_detailed_data(week: Optional[int] = None, team_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get detailed ESPN league data with all available views (like the ESPN web interface uses).
    
    Args:
        week: Optional week number for scoring data
        team_id: Optional team ID for specific roster data
        
    Returns:
        Dictionary containing comprehensive league data with live scoring, draft details, etc.
    """
    params = {
        "view": [
            "mDraftDetail",
            "mLiveScoring", 
            "mMatchupScore",
            "mPendingTransactions",
            "mPositionalRatings",
            "mRoster",
            "mSettings",
            "mTeam",
            "modular",
            "mNav"
        ]
    }
    if week:
        params["scoringPeriodId"] = week
    if team_id:
        params["rosterForTeamId"] = team_id
        
    return make_request(params)


def parse_cookies_from_file(filepath: str = "cookies.txt") -> Dict[str, str]:
    """
    Parse ESPN cookies from a text file containing cookie string.
    
    Args:
        filepath: Path to the file containing cookies (default: cookies.txt)
        
    Returns:
        Dictionary with 'espn_s2' and 'swid' keys
        
    Example cookies.txt format:
        Copy all cookies from browser dev tools (Application -> Cookies)
        Just paste the entire cookie string or individual cookies separated by semicolons
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract espn_s2
        espn_s2_match = re.search(r'espn_s2=([^;]+)', content)
        espn_s2 = espn_s2_match.group(1) if espn_s2_match else None
        
        # Extract SWID
        swid_match = re.search(r'SWID=(\{[^}]+\})', content)
        swid = swid_match.group(1) if swid_match else None
        
        return {
            'espn_s2': espn_s2,
            'swid': swid
        }
    except FileNotFoundError:
        return {'espn_s2': None, 'swid': None, 'error': f"File {filepath} not found"}
    except Exception as e:
        return {'espn_s2': None, 'swid': None, 'error': str(e)}


def test():
    # ===== CONFIGURATION =====
    TEAM_ID = 11  # Your team ID (optional)
    WEEK = 9  # Current week number
    
    # Load cookies from cookies.txt file (or set manually)
    print("Loading cookies from cookies.txt...")
    cookies = parse_cookies_from_file("cookies.txt")
    
    if 'error' in cookies:
        print(f"⚠ Warning: {cookies['error']}")
    
    # Update global variables with cookies from file
    if cookies.get('espn_s2'):
        ESPN_S2 = cookies.get('espn_s2')
    if cookies.get('swid'):
        SWID = cookies.get('swid')
    
    if ESPN_S2 and SWID:
        print(f"✓ Cookies loaded successfully")
        print(f"  SWID: {SWID}")
        print(f"  espn_s2: {ESPN_S2[:50]}..." if len(ESPN_S2) > 50 else f"  espn_s2: {ESPN_S2}")
    else:
        print("⚠ No cookies found - will only work for public leagues")
    
    # Fetch league data
    print(f"\nFetching league data...")
    print(f"League ID: {LEAGUE_ID}, Year: {YEAR}")
    
    try:
        # Get teams
        teams = get_teams()
        print(f"\n✓ Found {len(teams)} teams:")
        for team in teams:
            print(f"  - {team.get('name', 'Unknown')} (ID: {team.get('id')})")
        
        # Output team IDs for agent use
        print(f"\n🤖 Team ID Mapping (for agent use):")
        team_id_map = {}
        for team in teams:
            team_id = team.get('id')
            team_name = team.get('name', 'Unknown')
            team_id_map[team_name] = team_id
            print(f"  {team_name}: {team_id}")
        
        # Get standings
        standings = get_standings()
        print("\n📊 Standings:")
        for i, team in enumerate(standings, 1):
            record = team.get("record", {}).get("overall", {})
            wins = record.get("wins", 0)
            losses = record.get("losses", 0)
            ties = record.get("ties", 0)
            points = team.get("points", 0)
            print(f"  {i}. {team.get('name', 'Unknown')}: {wins}-{losses}-{ties} ({points:.1f} pts)")
        
        # Get detailed roster for your team
        print(f"\n👥 Getting roster for Team ID {TEAM_ID}...")
        roster_data = get_rosters(team_id=TEAM_ID)
        
        # Display roster
        teams_with_rosters = roster_data.get("teams", [])
        my_team_name = "Unknown Team"
        # Get team name from teams list
        for t in teams:
            if t.get("id") == TEAM_ID:
                my_team_name = t.get("name", "Unknown Team")
                break
        
        for team in teams_with_rosters:
            if team.get("id") == TEAM_ID:
                print(f"\n🏈 {my_team_name} Roster:")
                roster = team.get("roster", {})
                entries = roster.get("entries", [])
                
                if entries:
                    for entry in entries:
                        player = entry.get("playerPoolEntry", {}).get("player", {})
                        player_name = player.get("fullName", "Unknown Player")
                        position = entry.get("lineupSlotId", 0)
                        
                        # Map position IDs to names (common ESPN positions)
                        position_map = {
                            0: "QB", 1: "TQB", 2: "RB", 3: "RB/WR", 4: "WR",
                            5: "WR/TE", 6: "TE", 7: "OP", 8: "DT", 9: "DE",
                            10: "LB", 11: "DL", 12: "CB", 13: "S", 14: "DB",
                            15: "DP", 16: "D/ST", 17: "K", 20: "BENCH", 21: "IR",
                            23: "FLEX", 24: "ER"
                        }
                        position_name = position_map.get(position, f"POS_{position}")
                        
                        # Get stats if available
                        stats = player.get("stats", [])
                        points = 0
                        if stats:
                            for stat in stats:
                                if stat.get("statSourceId") == 0:  # Actual stats
                                    points = stat.get("appliedTotal", 0)
                                    break
                        
                        print(f"  [{position_name:6}] {player_name:30} ({points:.1f} pts)")
                else:
                    print("  No roster entries found")
                break
        
        # Get current matchups
        matchups = get_matchups(week=WEEK)
        print(f"\n⚔️  Week {WEEK} Matchups:")
        
        # Display matchups
        if matchups:
            displayed_matchups = set()  # Track displayed matchups to avoid duplicates
            
            for matchup in matchups:
                matchup_id = matchup.get("id")
                if matchup_id in displayed_matchups:
                    continue
                
                home = matchup.get("home", {})
                away = matchup.get("away", {})
                
                # Skip matchups that haven't started (both teams have 0 points)
                home_score = home.get("totalPoints", 0)
                away_score = away.get("totalPoints", 0)
                if home_score == 0 and away_score == 0:
                    continue
                    
                displayed_matchups.add(matchup_id)
                
                # Get team IDs
                home_team_id = home.get("teamId")
                away_team_id = away.get("teamId")
                
                # Find team names from the teams list
                home_name = "Unknown"
                away_name = "Unknown"
                for team in teams:
                    if team.get("id") == home_team_id:
                        home_name = team.get("name", "Unknown")
                    if team.get("id") == away_team_id:
                        away_name = team.get("name", "Unknown")
                
                # Determine winner/status
                winner_indicator = ""
                if home_score > away_score and home_score > 0:
                    winner_indicator = " ✓"
                elif away_score > home_score and away_score > 0:
                    winner_indicator = ""
                
                # Display matchup
                print(f"\n  {home_name}")
                print(f"    Score: {home_score:.1f}{winner_indicator if home_score > away_score else ''}")
                print(f"  vs")
                print(f"  {away_name}")
                print(f"    Score: {away_score:.1f}{winner_indicator if away_score > home_score else ''}")
        
        # Optional: Get detailed data with live scoring
        print("\n📡 Fetching detailed data with live scoring...")
        detailed = get_detailed_data(team_id=TEAM_ID)
        print(f"✓ Got detailed data with {len(detailed.get('teams', []))} teams")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tips:")
        print("  1. Make sure LEAGUE_ID is YOUR actual league ID from ESPN")
        print("  2. If the league is private, you need espn_s2 and SWID cookies")
        print("  3. Check that the season year is correct")

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()