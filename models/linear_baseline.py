import pandas as pd
from models.base import BaseModel

class LinearBaseline(BaseModel):
    @property
    def name(self) -> str:
        return "linear_baseline"
        
    def predict(self, features_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        """
        Baseline model: predicts upcoming gameweek points using rolling historical averages
        adjusted by the upcoming fixture difficulty and player availability chance.
        """
        predictions = []
        
        # We generate predictions for each week in the planning horizon
        for offset in range(horizon):
            for _, row in features_df.iterrows():
                # Difficulty adjustment
                diff = row.get("difficulty", 3.0)
                # Simple multiplier: higher difficulty lowers expected points
                difficulty_multiplier = max(0.2, (6.0 - diff) / 3.0)
                
                # Availability chance adjustment
                avail = row.get("chance_of_playing", 100.0) / 100.0
                
                avg_pts = row.get("avg_points_3gw", 0.0)
                avg_mins = row.get("avg_mins_3gw", 60.0)
                
                # Base expected values
                xp = avg_pts * difficulty_multiplier * avail
                xmins = avg_mins * avail
                
                predictions.append({
                    "player_id": int(row["player_id"]),
                    "gameweek_id": int(row.get("gameweek_id", 1)) + offset,
                    "projected_points": float(xp),
                    "projected_minutes": float(xmins)
                })
                
        return pd.DataFrame(predictions)
