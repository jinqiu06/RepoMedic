from repomedic.traceback_parser import parse_traceback


def test_trace_normal():
   text = r"""
Traceback (most recent call last):
File "D:\project\main.py", line 10, in <module>
calculate()
File "D:\project\calculator.py", line 5, in calculate
return 10 / 0
ZeroDivisionError: division by zero"""
   result = parse_traceback(text)

   assert result['file_path'] == r"D:\project\calculator.py"
def test_ifNone():
   text = ""
   result = parse_traceback(text)

   assert result == {}
def test_Error():
   text = r"""
Traceback (most recent call last):
File "D:\project\main.py", line 10, in <module>
calculate()
File "D:\project\calculator.py", line 5, in calculate
return 10 / 0
ValueError: invalid value: expected an integer
"""
   result = parse_traceback(text)

   assert result['error_type'] == 'ValueError'
   assert result['message'] == 'invalid value: expected an integer'