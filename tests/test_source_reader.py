from repomedic.source_reader import read_source_context

def test_read_normal(tmp_path):
    file = tmp_path / 'example.py'
    file.write_text("line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8\nline9\nline10\n",encoding = 'utf-8')

    result = read_source_context(
    project_root=str(tmp_path),
    file_path="example.py",
    line_number=5,
    context_lines=2
)
    assert result['start_line'] == 3
    assert result['end_line'] == 7
def test_read_at_beginning(tmp_path):
    file = tmp_path / 'example.py'
    file.write_text('line1\nline2\nline3\nline4\nline5\n',encoding = 'utf-8')

    result = read_source_context(
    project_root=str(tmp_path),
    file_path="example.py",
    line_number=1,
    context_lines=3
)
    assert result["start_line"] == 1
    assert result["end_line"] == 4
def test_path_outside_project(tmp_path):
    file = tmp_path / "example.py"
    file.write_text("hello", encoding="utf-8")

    project = tmp_path / "project"
    project.mkdir()

    result = read_source_context(
        project_root = str(project),
        file_path = '../example.py',
        line_number = 1,
        context_lines = 3
    )
    assert result is None
