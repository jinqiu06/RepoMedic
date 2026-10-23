import argparse
import sys
from pathlib import Path
import json
from repomedic.error_analyzer import analyze_error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = 'RepoMedic Python 错误诊断工具'
    )

    parser.add_argument(
        '--project-root',
        type = str,
        required = True,
        help = '待诊断项目的根目录'
    )

    parser.add_argument(
        '--traceback-file',
        type = str,
        required = True,
        help = '包含 python Traceback的文件路径'
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--agent", action="store_true", help="启用一轮源码调查和 AI 诊断")
    modes.add_argument(
    "--ai",
    action="store_true",
    help="启用 AI 诊断，将错误信息及相关源码发送到模型服务"
)

    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    project_root = Path(args.project_root)
    traceback_path = Path(args.traceback_file)

    # 1. 检查项目根目录
    if not project_root.is_dir():
        print(
            "错误：项目目录不存在或不是目录",
            file=sys.stderr
        )
        return 2

    # 2. 检查 Traceback 文件
    if not traceback_path.is_file():
        print(
            "错误:Traceback 文件不存在或不是普通文件",
            file=sys.stderr
        )
        return 2

    try:
        # 3. 检查文件大小
        file_size = traceback_path.stat().st_size

        if file_size > 1024 * 1024:
            print(
                "错误:Traceback 文件超过 1 MiB",
                file=sys.stderr
            )
            return 2

        # 4. 读取文件
        traceback_text = traceback_path.read_text(
            encoding="utf-8"
        )

    except (OSError, UnicodeError) as e:
        print(
            f"错误：读取 Traceback 文件失败：{e}",
            file=sys.stderr
        )
        return 2
    result = analyze_error(
        project_root=str(project_root.resolve()),
        traceback_text=traceback_text
)
    if result is None:
        print("错误：无法从 Traceback 中定位异常", file=sys.stderr)
        return 1
    if args.agent:
        from repomedic.agent_graph import run_agent

        state = run_agent(str(project_root.resolve()), result)
        if state.get("error_message"):
            print(state["error_message"], file=sys.stderr)
            return 3
        result["ai_diagnosis"] = state["diagnosis"].model_dump()
        result["investigation"] = {
            "decision": state["investigation_decision"].model_dump(),
            "search_results": state.get("search_results", []),
            "additional_context": state.get("additional_context", []),
            "warnings": state.get("warnings", []),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if not args.ai:
       print(json.dumps(result,ensure_ascii = False,indent = 2))
       return 0
    else:
        from repomedic.llm_client import diagnose_error, LLMServiceError
        from repomedic.config import get_load

        try:
           llm = get_load()
           answer = diagnose_error(result, llm)

        except LLMServiceError as exc:
           print(f"AI 诊断失败：{exc}", file=sys.stderr)
           return 3

        except RuntimeError:
           print("AI 模型配置或初始化失败", file=sys.stderr)
           return 3

        except ValueError:
           print("AI 诊断输入或响应格式无效", file=sys.stderr)
           return 3

        result["ai_diagnosis"] = answer.model_dump()

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
