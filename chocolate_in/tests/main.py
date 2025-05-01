import pytest
from unittest.mock import patch, MagicMock
from .main import (
    convert_dict_to_table,
    ensure_env_variables,
    get_project_config,
    handle_new_project,
    run,
    handle_package_installation,
    handle_reinstall,
    handle_env_action,
    handle_flags,
    custom_action,
    handle_path,
    handle_remove,
    handle_config,
    export,
)


@pytest.fixture
def mock_project_config():
    return {
        "startupEnv": ["VAR1", "VAR2"],
        "environmentVariables": {},
        "flagsString": "",
        "mainFile": "main.py",
        "requirements": [],
        "exclude": [],
    }


def test_convert_dict_to_table():
    data = {"key1": "value1", "key2": "value2"}
    table = convert_dict_to_table(data)
    assert table.row_count == 2
    assert table.columns[0].header == "key1"
    assert table.columns[1].header == "value1"


@patch("your_script.log")
def test_ensure_env_variables(mock_log, mock_project_config):
    with patch("your_script.get_project_config", return_value=mock_project_config):
        with patch("builtins.input", side_effect=["value1", "value2"]):
            ensure_env_variables()
            assert mock_project_config["environmentVariables"] == {
                "VAR1": "value1",
                "VAR2": "value2",
            }


@patch("your_script.log")
@patch("your_script.prj.get_config", return_value=None)
def test_get_project_config(mock_get_config, mock_log):
    with pytest.raises(SystemExit):
        get_project_config()


@patch("your_script.prj.setup_project")
@patch("your_script.log")
def test_handle_new_project(mock_log, mock_setup_project):
    class Args:
        pkgs = ["my_project", "main.py"]

    handle_new_project(Args())
    mock_setup_project.assert_called_once_with("my_project", "main.py")


@patch("your_script.log")
@patch("your_script.get_project_config")
def test_run(mock_get_project_config, mock_log):
    mock_get_project_config.return_value = {
        "environmentVariables": {},
        "mainFile": "main.py",
        "flagsString": "",
    }
    with patch("your_script.ensure_env_variables"), patch(
        "your_script.prj.VenvManager"
    ), patch("your_script.console.print"):
        run(Args(reinstall=False))


@patch("your_script.log")
@patch("your_script.prj.VenvManager")
def test_handle_package_installation(mock_venv, mock_log):
    mock_venv.return_value.install = MagicMock()
    packages = ["package1", "package2"]
    handle_package_installation(packages)
    assert mock_venv.return_value.install.call_count == 2


@patch("your_script.log")
@patch("your_script.get_project_config")
def test_handle_reinstall(mock_get_project_config, mock_log):
    mock_get_project_config.return_value = {"requirements": ["package1", "package2"]}
    with patch("your_script.prj.VenvManager"):
        handle_reinstall()


@patch("your_script.log")
def test_handle_env_action(mock_log):
    class Args:
        pkgs = ["list"]

    with patch("your_script.get_project_config", return_value=mock_project_config):
        handle_env_action(Args())
        assert mock_log.info.call_count > 0


@patch("your_script.log")
def test_handle_flags(mock_log):
    class Args:
        pkgs = ["--debug", "--verbose"]

    mock_config = {"flagsString": ""}
    with patch(
        "your_script.get_project_config", return_value=MagicMock(config=mock_config)
    ):
        handle_flags(Args())
        assert mock_config["flagsString"] == " ".join(Args.pkgs)


@patch("your_script.log")
def test_custom_action(mock_log):
    class Args:
        pkgs = ["add", "action_name", "command"]

    mock_project = MagicMock(config={"actions": {}})
    with patch("your_script.get_project_config", return_value=mock_project):
        custom_action(Args())
        assert "action_name" in mock_project.config["actions"]


@patch("your_script.log")
def test_handle_remove(mock_log):
    with patch("os.remove") as mock_remove:
        handle_remove(MagicMock())
        mock_remove.assert_called_once_with("CONFIG")


@patch("your_script.log")
def test_handle_config(mock_log):
    mock_project = MagicMock(config={"key": "value"})
    with patch("your_script.get_project_config", return_value=mock_project):
        handle_config(MagicMock())
        assert mock_log.info.call_count > 0


@patch("your_script.log")
def test_export(mock_log):
    class Args:
        output = "output.zip"

    mock_project = MagicMock(config={"name": "project_name", "exclude": []})
    with patch("your_script.get_project_config", return_value=mock_project):
        with patch("your_script.create_zip"):
            export(Args())
            assert mock_log.info.call_count > 0
