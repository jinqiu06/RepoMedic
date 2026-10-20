import re


def parse_traceback(traceback_text:str) -> dict:
    traceback_text = traceback_text.strip()
    if not traceback_text:
       return {}
    last_line = traceback_text.strip().splitlines()[-1]

    match1 = re.search(r'^([^:]+):\s*(.*)$',last_line)
    if not match1:
      return {}
    error_type,message = match1.group(1),match1.group(2)

    file_path = None
    line_number = None
    function = None

    for line in traceback_text.splitlines():
       match2 = re.search(
          r'File "([^"]+)", line (\d+), in (.+)',
          line
       )
       if match2:
        file_path = match2.group(1)
        line_number = int(match2.group(2))
        function = match2.group(3)
    return {
      'error_type':error_type,
      'message':message,
      'file_path':file_path,
      'line_number':line_number,
      'function':function
   }