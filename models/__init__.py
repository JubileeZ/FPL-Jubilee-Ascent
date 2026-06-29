import os
import importlib
import inspect
from pathlib import Path
from models.base import BaseModel

def get_model(model_name: str) -> BaseModel:
    """
    Auto-discovers and returns an instance of the requested model from the models/ folder.
    """
    models_dir = Path(__file__).resolve().parent
    
    # Scan models directory
    for file in os.listdir(models_dir):
        if file.endswith(".py") and file not in ["base.py", "__init__.py"]:
            module_name = f"models.{file[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # Look for subclasses of BaseModel
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModel) and obj is not BaseModel:
                        # Check name property or class attribute
                        # Instantiate to check instance name property
                        model_instance = obj()
                        if model_instance.name == model_name:
                            return model_instance
            except Exception:
                # Log or skip errors during imports
                continue
                
    raise ValueError(f"Model '{model_name}' not found. Please ensure it is implemented in the models/ directory.")
