import argparse
import json
import sys
from .core import APIError, OpenAIClient, Workflow, run_agent


def main():
    if len(sys.argv)>1 and sys.argv[1]=='produce':
        from .production import main as produce
        produce(sys.argv[2:])
        return
    parser = argparse.ArgumentParser(description='许老师聊健康 · ReAct 选题/制作/审核（不直接发布）')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('produce', help='用现有 Codex 登录执行 v3 参考与证据编辑流程；produce --help 查看参数')
    run = sub.add_parser('run', help='执行一次完整文字生产流程')
    run.add_argument('--brief', required=True)
    run.add_argument('--max-calls', type=int, default=18)
    backtest = sub.add_parser('backtest', help='50篇真实正文回测，rules或真实live API')
    backtest.add_argument('--mode', choices=['rules','live'], default='rules')
    backtest.add_argument('--dataset', default='data/backtest-50.json')
    backtest.add_argument('--annotations', default='benchmarks/annotations.json')
    backtest.add_argument('--out', default=None)
    sub.add_parser('check', help='检查环境，不发 API 请求')
    args = parser.parse_args()
    if args.command == 'check':
        import os,shutil
        print(json.dumps({'model': 'gpt-6.1-sol', 'reasoning': 'medium',
                          'codex_cli_available': bool(shutil.which('codex')),
                          'api_key_configured': bool(os.environ.get('OPENAI_API_KEY')),
                          'mobile_executor': 'Codex Mobile MCP handoff'}, ensure_ascii=False))
        return
    if args.command == 'backtest':
        from .backtest import run_rules, run_live
        try:
            runner = run_rules if args.mode == 'rules' else run_live
            result = runner(args.dataset, args.annotations, args.out or ('reports' if args.mode == 'rules' else 'data/live-backtest'))
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except (APIError, ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
        return
    flow = None
    try:
        if not 1 <= args.max_calls <= 50:
            raise ValueError('--max-calls 应在 1–50 之间')
        flow = Workflow(OpenAIClient(max_calls=args.max_calls))
        state = run_agent(flow, args.brief)
        print(json.dumps({'status': state['status'], 'artifacts': str(flow.dir),
                          'published': False}, ensure_ascii=False))
    except (APIError, ValueError, KeyError, TypeError, OSError) as exc:
        if flow:
            flow.state['last_error'] = str(exc)
            flow.save()
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
