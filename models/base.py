import abc
import pandas as pd

class BaseModel(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Unique identifier name for the model."""
        pass
        
    @abc.abstractmethod
    def predict(self, features_df: pd.DataFrame, horizon: int) -> pd.DataFrame:
        """
        Generate predictions for the planning horizon.
        
        Args:
            features_df: pd.DataFrame conforming to the FeatureContract.
            horizon: The planning horizon (number of gameweeks).
            
        Returns:
            pd.DataFrame matching the ProjectionContract:
                - player_id (int)
                - gameweek_id (int)
                - projected_points (float)
                - projected_minutes (float)
        """
        pass
