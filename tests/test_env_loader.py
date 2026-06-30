import os
from pathlib import Path
from clients.env_loader import load_env

def test_load_env_basic(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_KEY_BASIC=basic_value\n")
    
    # Ensure it's not already in environ
    if "TEST_KEY_BASIC" in os.environ:
        del os.environ["TEST_KEY_BASIC"]
        
    load_env(env_path=env_file)
    assert os.environ.get("TEST_KEY_BASIC") == "basic_value"
    del os.environ["TEST_KEY_BASIC"]

def test_load_env_quotes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TEST_KEY_DOUBLE=\"double_quoted\"\n"
        "TEST_KEY_SINGLE='single_quoted'\n"
    )
    
    for key in ["TEST_KEY_DOUBLE", "TEST_KEY_SINGLE"]:
        if key in os.environ:
            del os.environ[key]
            
    load_env(env_path=env_file)
    assert os.environ.get("TEST_KEY_DOUBLE") == "double_quoted"
    assert os.environ.get("TEST_KEY_SINGLE") == "single_quoted"
    
    del os.environ["TEST_KEY_DOUBLE"]
    del os.environ["TEST_KEY_SINGLE"]

def test_load_env_comments_and_empty_lines(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n"
        "# This is a comment\n"
        "TEST_KEY_VALID=valid_value\n"
        "  # Indented comment\n"
        "TEST_KEY_VALID2 = value2\n"
    )
    
    for key in ["TEST_KEY_VALID", "TEST_KEY_VALID2"]:
        if key in os.environ:
            del os.environ[key]
            
    load_env(env_path=env_file)
    assert os.environ.get("TEST_KEY_VALID") == "valid_value"
    assert os.environ.get("TEST_KEY_VALID2") == "value2"
    
    del os.environ["TEST_KEY_VALID"]
    del os.environ["TEST_KEY_VALID2"]

def test_load_env_do_not_overwrite(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_KEY_OVERWRITE=new_value\n")
    
    os.environ["TEST_KEY_OVERWRITE"] = "existing_value"
    
    load_env(env_path=env_file)
    assert os.environ.get("TEST_KEY_OVERWRITE") == "existing_value"
    del os.environ["TEST_KEY_OVERWRITE"]

def test_load_env_missing_file_does_not_raise():
    # Should complete without error
    load_env(env_path=Path("/nonexistent/path/.env"))
