from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import json

# Initialize FastMCP server
'''
The FastMCP class uses Python type hints and docstrings to automatically generate tool definitions, making it easy to create and maintain MCP tools.
'''
mcp = FastMCP("sleeper")

# Constants
SLEEPER_API_BASE = "https://api.sleeper.app/v1"
LEAGUE_ID="1182861335834730496"

async def make_sleeper_request(url: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    """Make a request to the Sleeper API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

@mcp.tool()
async def get_user(username: str) -> str:
    """Get Sleeper user information by username.
    
    Args:
        username: The username of the Sleeper user to look up.
    """
    url = f"{SLEEPER_API_BASE}/user/{username}"
    data = await make_sleeper_request(url)
    
    if data is None:
        return f"Unable to fetch user information for username: {username}"
    
    return f"""
User ID: {data.get('user_id', 'N/A')}
Username: {data.get('username', 'N/A')}
Display Name: {data.get('display_name', 'N/A')}
Avatar ID: {data.get('avatar', 'N/A')}
"""

@mcp.tool()
async def get_user_leagues(user_id: str, sport: str = "nfl", season: str = "2024") -> str:
    """Get all Sleeper leagues for a user in a specific sport and season.
    
    Args:
        user_id: The user ID to fetch leagues for.
        sport: The sport (default: "nfl").
        season: The season year (default: "2024").
    """
    url = f"{SLEEPER_API_BASE}/user/{user_id}/leagues/{sport}/{season}"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch leagues for user_id: {user_id}"
    
    if len(data) == 0:
        return f"No leagues found for user_id: {user_id} in {sport} {season}"
    
    leagues_info = []
    for league in data:
        league_info = f"""
League Name: {league.get('name', 'Unknown')}
League ID: {league.get('league_id', 'N/A')}
Status: {league.get('status', 'N/A')}
Total Rosters: {league.get('total_rosters', 'N/A')}
Season: {league.get('season', 'N/A')}
Draft ID: {league.get('draft_id', 'N/A')}
"""
        leagues_info.append(league_info)
    
    return "\n---\n".join(leagues_info)

@mcp.tool()
async def get_league(league_id: str = LEAGUE_ID) -> str:
    """Get detailed information about a specific Sleeper league.
    
    Args:
        league_id: The ID of the league to retrieve.
    """
    url = f"{SLEEPER_API_BASE}/league/{league_id}"
    data = await make_sleeper_request(url)
    
    if data is None:
        return f"Unable to fetch league information for league_id: {league_id}"
    
    return f"""
League Name: {data.get('name', 'Unknown')}
League ID: {data.get('league_id', 'N/A')}
Status: {data.get('status', 'N/A')}
Sport: {data.get('sport', 'N/A')}
Season: {data.get('season', 'N/A')}
Season Type: {data.get('season_type', 'N/A')}
Total Rosters: {data.get('total_rosters', 'N/A')}
Draft ID: {data.get('draft_id', 'N/A')}
Previous League ID: {data.get('previous_league_id', 'N/A')}
"""

@mcp.tool()
async def get_league_rosters(league_id: str = LEAGUE_ID) -> str:
    """Get all rosters in a Sleeper league.
    
    Args:
        league_id: The ID of the league to retrieve rosters from.
    """
    url = f"{SLEEPER_API_BASE}/league/{league_id}/rosters"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch rosters for league_id: {league_id}"
    
    if len(data) == 0:
        return f"No rosters found for league_id: {league_id}"
    
    rosters_info = []
    for roster in data:
        settings = roster.get('settings', {})
        roster_info = f"""
Roster ID: {roster.get('roster_id', 'N/A')}
Owner ID: {roster.get('owner_id', 'N/A')}
Wins: {settings.get('wins', 0)}
Losses: {settings.get('losses', 0)}
Ties: {settings.get('ties', 0)}
Points For: {settings.get('fpts', 0)}.{settings.get('fpts_decimal', 0)}
Points Against: {settings.get('fpts_against', 0)}.{settings.get('fpts_against_decimal', 0)}
Total Moves: {settings.get('total_moves', 0)}
Waiver Position: {settings.get('waiver_position', 'N/A')}
Player Count: {len(roster.get('players', []))}
"""
        rosters_info.append(roster_info)
    
    return "\n---\n".join(rosters_info)

@mcp.tool()
async def get_league_users(league_id: str = LEAGUE_ID) -> str:
    """Get all users in a Sleeper league.
    
    Args:
        league_id: The ID of the league to retrieve users from.
    """
    url = f"{SLEEPER_API_BASE}/league/{league_id}/users"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch users for league_id: {league_id}"
    
    if len(data) == 0:
        return f"No users found for league_id: {league_id}"
    
    users_info = []
    for user in data:
        metadata = user.get('metadata', {})
        user_info = f"""
User ID: {user.get('user_id', 'N/A')}
Username: {user.get('username', 'N/A')}
Display Name: {user.get('display_name', 'N/A')}
Team Name: {metadata.get('team_name', 'N/A')}
Is Commissioner: {user.get('is_owner', False)}
"""
        users_info.append(user_info)
    
    return "\n---\n".join(users_info)

@mcp.tool()
async def get_matchups(league_id: str = LEAGUE_ID, week: int = 9) -> str:
    """Get matchups for a specific week in a Sleeper league.
    
    Args:
        league_id: The ID of the league.
        week: The week number to get matchups for (1-18 for regular season).
    """
    url = f"{SLEEPER_API_BASE}/league/{league_id}/matchups/{week}"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch matchups for league_id: {league_id}, week: {week}"
    
    if len(data) == 0:
        return f"No matchups found for league_id: {league_id}, week: {week}"
    
    # Group matchups by matchup_id
    matchups_dict: dict[int, list] = {}
    for matchup in data:
        matchup_id = matchup.get('matchup_id')
        if matchup_id is not None:
            if matchup_id not in matchups_dict:
                matchups_dict[matchup_id] = []
            matchups_dict[matchup_id].append(matchup)
    
    matchups_info = []
    for matchup_id, teams in matchups_dict.items():
        matchup_str = f"Matchup {matchup_id}:\n"
        for team in teams:
            matchup_str += f"  Roster ID: {team.get('roster_id', 'N/A')}, Points: {team.get('points', 0)}\n"
        matchups_info.append(matchup_str)
    
    return "\n".join(matchups_info)

@mcp.tool()
async def get_user_drafts(user_id: str, sport: str = "nfl", season: str = "2024") -> str:
    """Get all Sleeper drafts for a user in a specific sport and season.
    
    Args:
        user_id: The user ID to fetch drafts for.
        sport: The sport (default: "nfl").
        season: The season year (default: "2024").
    """
    url = f"{SLEEPER_API_BASE}/user/{user_id}/drafts/{sport}/{season}"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch drafts for user_id: {user_id}"
    
    if len(data) == 0:
        return f"No drafts found for user_id: {user_id} in {sport} {season}"
    
    drafts_info = []
    for draft in data:
        draft_info = f"""
Draft ID: {draft.get('draft_id', 'N/A')}
Status: {draft.get('status', 'N/A')}
Type: {draft.get('type', 'N/A')}
Season: {draft.get('season', 'N/A')}
League ID: {draft.get('league_id', 'N/A')}
"""
        drafts_info.append(draft_info)
    
    return "\n---\n".join(drafts_info)

@mcp.tool()
async def get_draft(draft_id: str) -> str:
    """Get detailed information about a specific Sleeper draft.
    
    Args:
        draft_id: The ID of the draft to retrieve.
    """
    url = f"{SLEEPER_API_BASE}/draft/{draft_id}"
    data = await make_sleeper_request(url)
    
    if data is None:
        return f"Unable to fetch draft information for draft_id: {draft_id}"
    
    return f"""
Draft ID: {data.get('draft_id', 'N/A')}
Status: {data.get('status', 'N/A')}
Type: {data.get('type', 'N/A')}
Season: {data.get('season', 'N/A')}
League ID: {data.get('league_id', 'N/A')}
Sport: {data.get('sport', 'N/A')}
Settings:
  Rounds: {data.get('settings', {}).get('rounds', 'N/A')}
  Teams: {data.get('settings', {}).get('teams', 'N/A')}
"""

@mcp.tool()
async def get_draft_picks(draft_id: str) -> str:
    """Get all picks in a Sleeper draft.
    
    Args:
        draft_id: The ID of the draft to retrieve picks for.
    """
    url = f"{SLEEPER_API_BASE}/draft/{draft_id}/picks"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch picks for draft_id: {draft_id}"
    
    if len(data) == 0:
        return f"No picks found for draft_id: {draft_id}"
    
    picks_info = []
    for pick in data[:20]:  # Limit to first 20 picks for readability
        metadata = pick.get('metadata', {})
        pick_info = f"""
Pick #{pick.get('pick_no', 'N/A')} (Round {pick.get('round', 'N/A')}, Slot {pick.get('draft_slot', 'N/A')}):
  Player: {metadata.get('first_name', '')} {metadata.get('last_name', 'Unknown')}
  Position: {metadata.get('position', 'N/A')}
  Team: {metadata.get('team', 'N/A')}
  Picked by Roster: {pick.get('roster_id', 'N/A')}
"""
        picks_info.append(pick_info)
    
    if len(data) > 20:
        picks_info.append(f"... and {len(data) - 20} more picks")
    
    return "\n".join(picks_info)

@mcp.tool()
async def get_trending_players(sport: str = "nfl", trend_type: str = "add", lookback_hours: int = 24, limit: int = 25) -> str:
    """Get trending players on Sleeper based on add or drop activity.
    
    Args:
        sport: The sport (default: "nfl").
        trend_type: Either "add" or "drop" (default: "add").
        lookback_hours: Number of hours to look back (default: 24).
        limit: Number of results (default: 25).
    """
    url = f"{SLEEPER_API_BASE}/players/{sport}/trending/{trend_type}?lookback_hours={lookback_hours}&limit={limit}"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, list):
        return f"Unable to fetch trending {trend_type} players"
    
    if len(data) == 0:
        return f"No trending {trend_type} players found"
    
    trending_info = [f"Top {limit} Trending {trend_type.title()}s (Last {lookback_hours} hours):\n"]
    for i, player in enumerate(data, 1):
        trending_info.append(f"{i}. Player ID: {player.get('player_id', 'N/A')}, Count: {player.get('count', 0)}")
    
    return "\n".join(trending_info)

@mcp.tool()
async def get_all_players(sport: str = "nfl") -> str:
    """Get all NFL players in a Sleeper league.
    
    Args:
        sport: The sport (default: "nfl").
    """
    url = f"{SLEEPER_API_BASE}/players/{sport}"
    data = await make_sleeper_request(url)
    
    if data is None or not isinstance(data, dict):
        return f"Unable to fetch players for sport: {sport}"
    
    if len(data) == 0:
        return f"No players found for sport: {sport}"
    
    total_players = len(data)
    players_info = [f"Total Players: {total_players}\n"]
    
    for player_id, player in data.items():
        player_info = f"""
Player ID: {player_id}
Name: {player.get('first_name', '')} {player.get('last_name', 'Unknown')}
Position: {player.get('position', 'N/A')}
Team: {player.get('team', 'N/A')}
Number: {player.get('number', 'N/A')}
Status: {player.get('status', 'N/A')}
College: {player.get('college', 'N/A')}
Years Experience: {player.get('years_exp', 'N/A')}
"""
        players_info.append(player_info)
    
    return "\n---\n".join(players_info)

@mcp.tool()
async def get_nfl_state() -> str:
    """Get the current state of the NFL season from Sleeper (current week, season type, etc.)."""
    url = f"{SLEEPER_API_BASE}/state/nfl"
    data = await make_sleeper_request(url)
    
    if data is None:
        return "Unable to fetch NFL state information"
    
    return f"""
Season: {data.get('season', 'N/A')}
Season Type: {data.get('season_type', 'N/A')}
Week: {data.get('week', 'N/A')}
League Season: {data.get('league_season', 'N/A')}
League Create Season: {data.get('league_create_season', 'N/A')}
Display Week: {data.get('display_week', 'N/A')}
"""

def test():
    import asyncio
    result = asyncio.run(get_all_players())
    print(result)

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    # test()
    main()

# TODO: Since getting all players is a large list, we should do RAG instead and use that to get the player id --> name/info mapping
# We can check on initialization of the RAG if it is old, and repull it if it is.