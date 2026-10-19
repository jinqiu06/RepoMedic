from repomedic.error_analyzer import analyze_error

def test_example(tmp_path):
    test_file = tmp_path / 'calculator.py'

    test_file.write_text(
        'a = 1\nb=0\nprint(a / b)\n',
        encoding = 'utf-8'
    )
    traceback_text = f'''Traceback (most recent call last):
  File "{test_file}", line 3, in <module>
    print(a / b)
ZeroDivisionError: division by zero'''

    result = analyze_error(str(tmp_path),traceback_text)

    assert result['error_type'] == 'ZeroDivisionError'
    assert result['line_number'] == 3

def test_if_empty(tmp_path):
    test_file = tmp_path / 'calculator.py'

    test_file.write_text(
        'a = 1\nb=0\nprint(a / b)\n',
        encoding = 'utf-8'
    )

    traceback_text = ""

    result = analyze_error(str(tmp_path),traceback_text)

    assert result == None
def test_if_exists(tmp_path):
    test_file = tmp_path / 'calculator.py'
    
    test_file.write_text(
            'a = 1\nb=0\nprint(a / b)\n',
            encoding = 'utf-8'
        )

    traceback_text = f'''Traceback (most recent call last):
  File "missing_file", line 3, in <module>
    print(a / b)
ZeroDivisionError: division by zero'''
    result = analyze_error(str(tmp_path),traceback_text)

    assert result['source_context'] == None
    assert result["error_type"] == "ZeroDivisionError"