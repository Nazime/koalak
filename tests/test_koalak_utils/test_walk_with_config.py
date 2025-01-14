import json

from koalak.utils import walk_with_config


def test_walk_with_config_simple_case(tmp_path):
    """
    Directory structure for the test:
    /root_dir
        ├── config.json
        ├── file1.txt
    """
    # Create a temporary directory for the test
    root_dir = tmp_path

    # Setup: Create config and file
    config_file = root_dir / "config.json"
    config_file.write_text(json.dumps({"key": "root_config"}))

    file1 = root_dir / "file1.txt"
    file1.write_text("content")

    # Call the function with real JSON parsing
    result = list(walk_with_config(root_dir, config_filename="config.json"))

    # Check the configuration yielded
    assert len(result) == 1  # Should have 1 directory
    root, dirs, files, config = result[0]
    assert root == str(root_dir)
    assert dirs == []
    assert set(files) == {"config.json", "file1.txt"}
    assert config == {"key": "root_config"}


def test_walk_with_config_multiple_configs(tmp_path):
    """
    Directory structure for the test:
    /root_dir
        ├── conf.json
        ├── file1.txt
        ├── subdir
            ├── conf.json
            └── file2.txt
    """

    # Create a temporary directory for the test
    root_dir = tmp_path

    # Setup: Create the root config and files
    root_conf_file = root_dir / "conf.json"
    root_conf_file.write_text(json.dumps({"key1": "root_config", "key2": 200}))

    file1 = root_dir / "file1.txt"
    file1.write_text("content")

    # Create subdir and its config file
    subdir = root_dir / "subdir"
    subdir.mkdir()

    sub_conf_file = subdir / "conf.json"
    sub_conf_file.write_text(json.dumps({"key2": 300}))

    file2 = subdir / "file2.txt"
    file2.write_text("more content")

    # Call the function with real JSON parsing
    result = list(walk_with_config(root_dir, config_filename="conf.json"))

    # Check the configurations yielded
    assert len(result) == 2  # Should have 2 directories

    # First directory (root)
    root, dirs, files, config = result[0]
    assert root == str(root_dir)
    assert dirs == ["subdir"]
    assert set(files) == {"conf.json", "file1.txt"}
    assert config == {"key1": "root_config", "key2": 200}

    # Second directory (subdir)
    subdir, dirs, files, config = result[1]
    assert subdir == str(subdir)
    assert dirs == []
    assert set(files) == {"conf.json", "file2.txt"}
    assert config == {"key1": "root_config", "key2": 300}


def test_walk_with_config_complex_structure(tmp_path):
    """
    Directory structure for the test:
    /root_dir
        ├── conf.json
        ├── file1.txt
        ├── subdir1
        │   ├── conf.json
        │   └── file2.txt
        └── subdir2
            ├── file3.txt
            └── subsubdir
                ├── conf.json
                └── file4.txt
    """

    # Create a temporary directory for the test
    root_dir = tmp_path

    # Setup: Create the root config and files
    root_conf_file = root_dir / "conf.json"
    root_conf_file.write_text(json.dumps({"name": "root_dir", "speed": 200}))

    file1 = root_dir / "file1.txt"
    file1.write_text("content")

    # Create subdir1 and its config file
    subdir1 = root_dir / "subdir1"
    subdir1.mkdir()

    subdir1_conf_file = subdir1 / "conf.json"
    subdir1_conf_file.write_text(
        json.dumps(
            {
                "name": "subdir1",
                "subdir1_key": True,
                "speed": 300,
            }
        )
    )

    file2 = subdir1 / "file2.txt"
    file2.write_text("more content")

    # Create subdir2 and its files (without config file)
    subdir2 = root_dir / "subdir2"
    subdir2.mkdir()

    file3 = subdir2 / "file3.txt"
    file3.write_text("even more content")

    # Create subsubdir under subdir2 and its config file
    subsubdir = subdir2 / "subsubdir"
    subsubdir.mkdir()

    subsubdir_conf_file = subsubdir / "conf.json"
    subsubdir_conf_file.write_text(
        json.dumps({"name": "subsubdir", "speed": 500, "subsubdir_key": True})
    )

    file4 = subsubdir / "file4.txt"
    file4.write_text("subsubdir content")

    # Call the function with real JSON parsing
    result = list(walk_with_config(root_dir, config_filename="conf.json"))

    # Sort the result to make the order predictable
    result.sort(key=lambda x: x[0])  # Sort by directory path (root)

    # Check the configurations yielded
    assert len(result) == 4  # Should have 4 directories

    # First directory (root)
    root, dirs, files, config = result[0]
    assert root == str(root_dir)
    assert set(dirs) == {"subdir1", "subdir2"}
    assert set(files) == {"conf.json", "file1.txt"}
    assert config == {"name": "root_dir", "speed": 200}

    # Second directory (subdir1)
    root, dirs, files, config = result[1]
    assert root == f"{root_dir}/subdir1"
    assert dirs == []
    assert set(files) == {"conf.json", "file2.txt"}
    assert config == {
        "name": "subdir1",
        "subdir1_key": True,
        "speed": 300,
    }

    # Third directory (subdir2, no config file, inherits root's config)
    root, dirs, files, config = result[2]
    assert root == f"{root_dir}/subdir2"
    assert dirs == ["subsubdir"]
    assert set(files) == {"file3.txt"}
    assert config == {"name": "root_dir", "speed": 200}

    # Fourth directory (subsubdir, inherits subdir2's config + its own config)
    root, dirs, files, config = result[3]
    assert root == f"{root_dir}/subdir2/subsubdir"
    assert dirs == []
    assert set(files) == {"conf.json", "file4.txt"}
    assert config == {"name": "subsubdir", "speed": 500, "subsubdir_key": True}


def test_walk_with_config_list_merge(tmp_path):
    """
    Directory structure for the test:
    /root_dir
        ├── conf.json
        ├── subdir
        │   └── conf.json
    """

    # Create a temporary directory for the test
    root_dir = tmp_path

    # Setup: Create the root config and files
    root_conf_file = root_dir / "conf.json"
    root_conf_file.write_text(json.dumps({"tags": ["a"]}))

    # Create subdir and its config file
    subdir = root_dir / "subdir"
    subdir.mkdir()

    subdir_conf_file = subdir / "conf.json"
    subdir_conf_file.write_text(json.dumps({"tags": ["b"]}))

    # Call the function with real JSON parsing
    result = list(walk_with_config(root_dir, config_filename="conf.json"))

    # Sort the result to make the order predictable
    result.sort(key=lambda x: x[0])  # Sort by directory path (root)

    # Check the configurations yielded
    assert len(result) == 2  # Should have 2 directories

    # First directory (root)
    root, dirs, files, config = result[0]
    assert root == str(root_dir)
    assert set(dirs) == {"subdir"}
    assert set(files) == {"conf.json"}
    assert config == {"tags": ["a"]}

    # Second directory (subdir)
    root, dirs, files, config = result[1]
    assert root == str(subdir)
    assert dirs == []
    assert set(files) == {"conf.json"}
    assert config == {"tags": ["a", "b"]}  # Tags from root + subdir
