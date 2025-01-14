import pytest
from koalak.config import Config


def test_config_initialization(tmp_path):
    temp_file = tmp_path / "config.toml"
    config = Config(temp_file)
    assert isinstance(config, Config)
    assert config.path == temp_file


def test_simple_read_section_then_write(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[database]
user='admin'
password='secret'
"""
        )

    config = Config(temp_file)
    db_conf = config["database"]
    assert db_conf["user"] == "admin"
    assert db_conf["password"] == "secret"

    # Now change it
    db_conf["password"] = "admin123"
    # Create new one
    db_conf["port"] = 3333

    config = Config(temp_file)

    db_conf = config["database"]
    assert db_conf["user"] == "admin"
    assert db_conf["password"] == "admin123"
    assert db_conf["port"] == 3333


def test_simple_read_section_then_remove(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[database]
user='admin'
password='secret'
"""
        )

    config = Config(temp_file)
    db_conf = config["database"]
    assert "user" in db_conf
    del db_conf["user"]
    assert "user" not in db_conf
    with pytest.raises(KeyError):
        user = db_conf["user"]

    config = Config(temp_file)
    db_conf = config["database"]
    assert "user" not in db_conf
    assert "user" not in db_conf
    with pytest.raises(KeyError):
        user = db_conf["user"]


def test_2_sections_editing_the_config(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[alpha]
user='admin'
password='secret'

[beta]
user='john'
password='smith'

"""
        )

    config = Config(temp_file)
    config_alpha = config["alpha"]
    config_beta = config["beta"]

    assert config_alpha["user"] == "admin"
    config_alpha["user"] = "admin2"
    assert config_beta["user"] == "john"
    config_beta["user"] = "john2"

    # Check that after loading everything is good
    config = Config(temp_file)
    config_alpha = config["alpha"]
    config_beta = config["beta"]
    assert config_alpha["user"] == "admin2"
    assert config_beta["user"] == "john2"


def test_nested_sections(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[main]
[main.database]
user='admin'
password='secret'
"""
        )

    config = Config(temp_file)
    main_db_config = config["main"]["database"]
    assert main_db_config["user"] == "admin"

    # Modify and save
    main_db_config["password"] = "new_secret"

    # Reload and check
    new_config = Config(temp_file)
    new_main_db_config = new_config["main"]["database"]
    assert new_main_db_config["password"] == "new_secret"


def test_type_preservation(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[settings]
number=10
flag=true
"""
        )

    config = Config(temp_file)
    assert isinstance(config["settings"]["number"], int)
    assert isinstance(config["settings"]["flag"], bool)

    # Modify and save
    config["settings"]["number"] = 20
    config["settings"]["flag"] = False
    config.save()

    # Reload and check
    new_config = Config(temp_file)
    assert new_config["settings"]["number"] == 20
    assert new_config["settings"]["flag"] is False


def test_initialization_with_default_data(tmp_path):
    temp_file = tmp_path / "config.toml"
    default_data = {"default_section": {"key1": "value1", "key2": 2}}

    config = Config(temp_file, default_data=default_data)
    assert config["default_section"]["key1"] == "value1"
    assert config["default_section"]["key2"] == 2


def test_default_data_not_overwritten(tmp_path):
    temp_file = tmp_path / "config.toml"
    with open(temp_file, "w") as f:
        f.write(
            """[default_section]
key1 = "existing_value"
"""
        )
    default_data = {"default_section": {"key1": "default_value", "key2": 2}}

    config = Config(temp_file, default_data=default_data)
    assert config["default_section"]["key1"] == "existing_value"
    assert config["default_section"]["key2"] == 2


def test_default_data_with_nested_sections(tmp_path):
    temp_file = tmp_path / "config.toml"
    default_data = {"section": {"sub_section": {"key": "value"}}}

    config = Config(temp_file, default_data=default_data)
    assert config["section"]["sub_section"]["key"] == "value"


def test_default_data_persistence_after_save(tmp_path):
    temp_file = tmp_path / "config.toml"
    default_data = {"section": {"key": "value"}}

    config = Config(temp_file, default_data=default_data)

    new_config = Config(temp_file)
    assert new_config["section"]["key"] == "value"
