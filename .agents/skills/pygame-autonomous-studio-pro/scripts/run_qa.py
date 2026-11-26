"""Run Miopia's real suite with a disposable profile and a bounded timeout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('pytest_args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.out.resolve()
    if not (repo/'src/main.py').is_file() or not (repo/'tests').is_dir():
        parser.error('Expected Miopia root with src/main.py and tests/')
    if args.timeout <= 0:
        parser.error('Timeout must be positive')
    out.mkdir(parents=True, exist_ok=True)
    candidates = [repo/'.venv/bin/python', repo/'.venv/Scripts/python.exe']
    python = next((str(p) for p in candidates if p.exists()), sys.executable)
    extra = args.pytest_args[1:] if args.pytest_args[:1] == ['--'] else args.pytest_args
    command = [python, '-B', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *extra]
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix='miopia-studio-qa-') as profile:
        env = os.environ.copy()
        env.update(MIOPIA_DADOS=profile, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy',
                   PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        try:
            result = subprocess.run(command, cwd=repo, env=env, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=args.timeout, check=False)
            code, log, timed_out = result.returncode, result.stdout, False
        except subprocess.TimeoutExpired as exc:
            code, timed_out = 124, True
            log = exc.stdout or ''
            if isinstance(log, bytes): log = log.decode('utf-8', errors='replace')
            log += '\nTIMEOUT: execution ended before suite completion.\n'
    (out/'pytest.log').write_text(log, encoding='utf-8')
    report = {'command': command, 'repo': str(repo), 'exit_code': code,
              'timed_out': timed_out, 'seconds': round(time.perf_counter()-started, 3),
              'profile': 'disposable, removed', 'log': 'pytest.log',
              'scope': extra or ['full existing suite']}
    (out/'qa_result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(log)
    print(json.dumps(report, ensure_ascii=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
