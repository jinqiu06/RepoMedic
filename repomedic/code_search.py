import ast
import os
from pathlib import Path


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
}

MAX_FILE_SIZE = 1024 * 1024  # 1 MiB


def search_symbol(
    project_root: str | Path,
    symbol: str,
    max_results: int = 20
) -> list[dict]:

    root = Path(project_root).resolve()

    if not root.is_dir():
        raise ValueError("项目目录不存在")

    if not isinstance(symbol, str) or not symbol.isidentifier():
        raise ValueError("符号名称不合法")

    if type(max_results) is not int or max_results <= 0:
        raise ValueError("max_results 必须是正整数")

    results = []

    for dirpath, dirnames, filenames in os.walk(root):

        # 排除无关目录及符号链接目录
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in EXCLUDED_DIRS
            and not (Path(dirpath) / d).is_symlink()
        )

        for filename in sorted(filenames):

            if not filename.endswith(".py"):
                continue

            file_path = Path(dirpath) / filename

            try:
                # 跳过符号链接文件
                if file_path.is_symlink():
                    continue

                # 防止越界读取
                resolved_path = file_path.resolve()
                if not resolved_path.is_relative_to(root):
                    continue

                if not file_path.is_file():
                    continue

                # 跳过超大文件
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                code = file_path.read_text(encoding="utf-8")
                tree = ast.parse(code)

            except (OSError, UnicodeError, SyntaxError, RecursionError):
                # 跳过无法正常处理的文件
                continue

            # 遍历当前文件的 AST
            for node in ast.walk(tree):

                if not isinstance(
                    node,
                    (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    continue

                if node.name != symbol:
                    continue

                if isinstance(node, ast.ClassDef):
                    kind = "class"
                elif isinstance(node, ast.AsyncFunctionDef):
                    kind = "async_function"
                else:
                    kind = "function"

                results.append({
                    "file_path": file_path.relative_to(root).as_posix(),
                    "name": node.name,
                    "kind": kind,
                    "line_number": node.lineno
                })

                if len(results) >= max_results:
                    return results

    return results
