import json
from pathlib import Path
from repomedic.cli import main

def test_cli_success(tmp_path: Path, capsys) -> None:
    # 创建临时项目
    project = tmp_path / "project"
    project.mkdir()

    source_file = project / "calculator.py"
    source_file.write_text(
        "def divide(a, b):\n"
        "    return a / b\n"
        "\n"
        "divide(10, 0)\n",
        encoding="utf-8"
    )

    # 创建 Traceback 文件
    traceback_file = tmp_path / "error.log"
    traceback_file.write_text(
        "Traceback (most recent call last):\n"
        f'  File "{source_file}", line 2, in divide\n'
        "    return a / b\n"
        "ZeroDivisionError: division by zero\n",
        encoding="utf-8"
    )

    # 执行 CLI
    exit_code = main([
        "--project-root", str(project),
        "--traceback-file", str(traceback_file)
    ])

    # 捕获输出
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""

    result = json.loads(captured.out)

    assert result["error_type"] == "ZeroDivisionError"
    assert result["line_number"] == 2
    assert result["source_context"] is not None
    assert result["source_context"]["code"][1].strip() == "return a / b"
def test_cli_invalid_project(tmp_path: Path, capsys):
    missing_project = tmp_path / "missing_project"

    exit_code = main([
        "--project-root", str(missing_project),
        "--traceback-file", str(tmp_path / "error.log")
    ])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "项目目录" in captured.err


def test_cli_missing_traceback(tmp_path: Path, capsys):
    project = tmp_path / "project"
    project.mkdir()

    missing_file = tmp_path / "missing.log"

    exit_code = main([
        "--project-root", str(project),
        "--traceback-file", str(missing_file)
    ])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Traceback 文件" in captured.err


def test_cli_traceback_is_directory(tmp_path: Path, capsys):
    project = tmp_path / "project"
    project.mkdir()

    exit_code = main([
        "--project-root", str(project),
        "--traceback-file", str(project)
    ])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Traceback 文件" in captured.err
def test_cli_oversized_traceback(tmp_path:Path,capsys): 
    project = tmp_path / "project"
    project.mkdir()

    traceback_file = tmp_path / "large.log"
    traceback_file.write_text(
    "A" * (1024 * 1024 + 1),
    encoding="utf-8"
)

    exit_code = main([
        "--project-root", str(project),
        "--traceback-file", str(traceback_file)
    ])

    captured = capsys.readouterr()

    assert exit_code == 2
    assert "超过 1 MiB" in captured.err    