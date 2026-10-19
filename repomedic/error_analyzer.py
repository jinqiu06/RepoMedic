from repomedic.traceback_parser import parse_traceback
from repomedic.source_reader import read_source_context

def analyze_error(project_root:str,traceback_text:str) -> dict | None:
    error_info = parse_traceback(traceback_text)

    if not error_info:
        return None
    file_path = error_info['file_path']
    line_number = error_info['line_number']

    if not file_path or not line_number:
        return None
    error_info['source_context'] = read_source_context(
        project_root,file_path,line_number
    )

    return error_info

    
