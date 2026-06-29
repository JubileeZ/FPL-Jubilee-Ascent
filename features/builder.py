import pandas as pd
from pathlib import Path
from typing import Optional

def build_features(processed_dir: Path, target_gw: int) -> pd.DataFrame:
    """
    Compiles a FeatureContract DataFrame for a target gameweek.
    
    Contains historical rolling stats and upcoming fixture metadata.
    """
    # 1. Load Parquet tables
    df_players = pd.read_parquet(processed_dir / "players.parquet")
    df_fixtures = pd.read_parquet(processed_dir / "fixtures.parquet")
    df_clubs = pd.read_parquet(processed_dir / "clubs.parquet")
    
    perf_path = processed_dir / "player_performances.parquet"
    if perf_path.exists():
        df_perf = pd.read_parquet(perf_path)
    else:
        df_perf = pd.DataFrame(columns=["player_id", "gameweek_id", "total_points", "minutes"])

    df_players = df_players.rename(columns={"id": "player_id"})
    
    # 2. Compute historical features (e.g. rolling averages before target_gw)
    df_hist = df_perf[df_perf["gameweek_id"] < target_gw]
    
    # Simple rolling GW averages
    rolling_stats = []
    for pid in df_players["player_id"].unique():
        p_hist = df_hist[df_hist["player_id"] == pid].sort_values("gameweek_id", ascending=False)
        if len(p_hist) > 0:
            avg_pts_3gw = p_hist.head(3)["total_points"].mean()
            avg_mins_3gw = p_hist.head(3)["minutes"].mean()
        else:
            avg_pts_3gw = 0.0
            avg_mins_3gw = 0.0
        rolling_stats.append({
            "player_id": pid,
            "avg_points_3gw": float(avg_pts_3gw),
            "avg_mins_3gw": float(avg_mins_3gw)
        })
    df_rolling = pd.DataFrame(rolling_stats)

    # 3. Merge player metadata
    df_feat = df_players.merge(df_rolling, on="player_id", how="left")
    
    # 4. Map strength from clubs
    df_clubs_sub = df_clubs[["id", "strength"]].rename(columns={"id": "club_id", "strength": "team_strength"})
    df_feat = df_feat.merge(df_clubs_sub, on="club_id", how="left")

    # 5. Extract upcoming fixtures for target_gw
    df_target_fixtures = df_fixtures[df_fixtures["gameweek_id"] == target_gw]
    
    # Build maps for home/away fixtures
    fixture_maps = []
    for _, f in df_target_fixtures.iterrows():
        # Home team perspective
        fixture_maps.append({
            "club_id": f["home_club_id"],
            "opponent_id": f["away_club_id"],
            "is_home": True,
            "difficulty": f["team_h_difficulty"]
        })
        # Away team perspective
        fixture_maps.append({
            "club_id": f["away_club_id"],
            "opponent_id": f["home_club_id"],
            "is_home": False,
            "difficulty": f["team_a_difficulty"]
        })
    df_fmap = pd.DataFrame(fixture_maps)
    
    df_feat = df_feat.merge(df_fmap, on="club_id", how="left")
    
    # Fill NAs
    df_feat["is_home"] = df_feat["is_home"].fillna(False)
    df_feat["difficulty"] = df_feat["difficulty"].fillna(3.0)
    df_feat["opponent_id"] = df_feat["opponent_id"].fillna(0).astype(int)
    
    # Define chance of playing
    df_feat["chance_of_playing"] = df_feat["chance_of_playing_next_round"].fillna(100.0)
    
    df_feat["gameweek_id"] = target_gw
    
    return df_feat
