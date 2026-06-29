import json
import pandas as pd
from features.processor import process_directory

def test_process_directory(tmp_path):
    input_dir = tmp_path / "raw"
    output_dir = tmp_path / "processed"
    input_dir.mkdir()
    
    # Mock bootstrap static data
    bootstrap_data = {
        "teams": [
            {"id": 1, "name": "Arsenal", "short_name": "ARS", "strength": 4}
        ],
        "events": [
            {"id": 1, "name": "Gameweek 1", "deadline_time": "2026-08-11T17:30:00Z", "finished": True, "is_current": True}
        ],
        "elements": [
            {"id": 1, "first_name": "Martin", "second_name": "Odegaard", "web_name": "Odegaard", "team": 1, "element_type": 3, "now_cost": 85, "status": "a"}
        ]
    }
    with open(input_dir / "bootstrap_static.json", "w") as f:
        json.dump(bootstrap_data, f)
        
    # Mock fixtures data
    fixtures_data = [
        {"id": 1, "event": 1, "kickoff_time": "2026-08-11T19:00:00Z", "team_h": 1, "team_a": 2, "finished": True, "started": True, "team_h_score": 2, "team_a_score": 1, "team_h_difficulty": 3, "team_a_difficulty": 4}
    ]
    with open(input_dir / "fixtures_all.json", "w") as f:
        json.dump(fixtures_data, f)
        
    # Process
    process_directory(input_dir, output_dir)
    
    # Check outputs
    assert (output_dir / "clubs.parquet").exists()
    assert (output_dir / "gameweeks.parquet").exists()
    assert (output_dir / "players.parquet").exists()
    assert (output_dir / "fixtures.parquet").exists()
    
    # Verify contents
    df_clubs = pd.read_parquet(output_dir / "clubs.parquet")
    assert len(df_clubs) == 1
    assert df_clubs.loc[0, "name"] == "Arsenal"
    
    df_players = pd.read_parquet(output_dir / "players.parquet")
    assert len(df_players) == 1
    assert df_players.loc[0, "club_id"] == 1
    assert df_players.loc[0, "position_id"] == 3
