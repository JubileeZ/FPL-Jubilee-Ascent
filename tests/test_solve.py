import pandas as pd
from commands.solve import build_my_data_from_parquet

def test_build_my_data_from_parquet(tmp_path):
    # 1. Create mock processed tables
    df_picks = pd.DataFrame([
        {"player_id": 101, "purchase_price": 95, "selling_price": 98, "lineup_index": 1, "multiplier": 1, "is_captain": False, "is_vice_captain": False}
    ])
    df_picks.to_parquet(tmp_path / "user_picks.parquet")
    
    df_state = pd.DataFrame([
        {"entry_id": 12345, "bank": 15, "free_transfers": 2, "value": 1000, "active_chip": None}
    ])
    df_state.to_parquet(tmp_path / "user_state.parquet")
    
    df_players = pd.DataFrame([
        {"id": 101, "position_id": 3}
    ])
    df_players.to_parquet(tmp_path / "players.parquet")
    
    # 2. Build my_data dict
    my_data = build_my_data_from_parquet(tmp_path)
    
    assert my_data["team_id"] == 12345
    assert my_data["transfers"]["bank"] == 15
    assert my_data["transfers"]["limit"] == 2
    assert len(my_data["picks"]) == 1
    assert my_data["picks"][0]["element"] == 101
    assert my_data["picks"][0]["selling_price"] == 98
    assert my_data["picks"][0]["element_type"] == 3

def test_build_my_data_with_unlimited_transfers(tmp_path):
    # 1. Create mock processed tables
    df_picks = pd.DataFrame([
        {"player_id": 101, "purchase_price": 95, "selling_price": 98, "lineup_index": 1, "multiplier": 1, "is_captain": False, "is_vice_captain": False}
    ])
    df_picks.to_parquet(tmp_path / "user_picks.parquet")
    
    df_state = pd.DataFrame([
        {"entry_id": 12345, "bank": 15, "free_transfers": None, "value": 1000, "active_chip": None}
    ])
    df_state.to_parquet(tmp_path / "user_state.parquet")
    
    df_players = pd.DataFrame([
        {"id": 101, "position_id": 3}
    ])
    df_players.to_parquet(tmp_path / "players.parquet")
    
    # 2. Build my_data dict
    my_data = build_my_data_from_parquet(tmp_path)
    
    assert my_data["transfers"]["limit"] is None
