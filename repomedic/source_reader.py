from pathlib import Path

def read_source_context(
        project_root:str,
        file_path:str,
        line_number:int,
        context_lines:int = 5
) -> dict | None:
    try:
        path = (Path(project_root).resolve() / file_path).resolve()
        if not path.is_relative_to(Path(project_root).resolve()):
            return None
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            return None
        return _read_source_context(project_root, file_path, line_number, context_lines)
    except (OSError, UnicodeError, ValueError):
        return None


def _read_source_context(
        project_root:str,
        file_path:str,
        line_number:int,
        context_lines:int = 5
) ->dict | None:
    if line_number < 1 or context_lines < 0:
       return None

    root = Path(project_root).resolve()
    path = (root / file_path).resolve()

    if not path.is_relative_to(root):
        return None
    if not path.exists() or not path.is_file():
        return None


    context = []
    start = max(1,line_number - context_lines)
    end = line_number + context_lines

    with open(path,'r',encoding = 'utf-8') as f:
        for line,content in enumerate(f,start = 1):
            if line > end:
                break
            if line >= start:
                context.append(content.rstrip('\r\n'))
        if not context:
            return None

        actual_end = start + len(context) - 1
        if actual_end < line_number:
            return None

    return {
        'path_file':file_path,
        'start_line':start,
        'end_line':actual_end,
        'code':context
    }




