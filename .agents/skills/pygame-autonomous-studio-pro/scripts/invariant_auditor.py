"""Find review candidates in Python source without importing or modifying it."""
import argparse
import ast
import json
from pathlib import Path

FRAME_FUNCTIONS = {'update', 'draw', 'render', 'step', 'main_loop', 'rodar',
                   'atualizar', 'desenhar', 'renderizar'}
ASSET_CALLS = {'pygame.image.load', 'pygame.font.Font', 'pygame.font.SysFont',
               'pygame.mixer.Sound', 'pygame.mixer.music.load'}
EXCLUDED = {'.git', '.venv', 'venv', '__pycache__', '.agents', 'distribuicao',
            'colaboracao', 'outputs', 'tests', 'runtime', 'node_modules'}


class Auditor(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.aliases = {}
        self.functions = []
        self.loop_depth = 0
        self.issues = []

    def visit_Import(self, node):
        for item in node.names:
            self.aliases[item.asname or item.name.split('.')[0]] = item.name if item.asname else item.name.split('.')[0]

    def visit_ImportFrom(self, node):
        if node.level == 0:
            for item in node.names:
                self.aliases[item.asname or item.name] = f'{node.module}.{item.name}'

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        old_loop = self.loop_depth
        self.loop_depth = 0
        self.generic_visit(node)
        self.loop_depth = old_loop
        self.functions.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_While(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    visit_For = visit_While
    visit_AsyncFor = visit_While

    def canonical(self, node):
        if isinstance(node, ast.Name):
            return self.aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            return f'{self.canonical(node.value)}.{node.attr}'
        return ''

    def visit_Call(self, node):
        name = self.canonical(node.func)
        current = self.functions[-1] if self.functions else '<module>'
        hot_path = current in FRAME_FUNCTIONS or (not self.functions and self.loop_depth > 0)
        code = ('ASSET_IN_FRAME' if name in ASSET_CALLS else
                'BLOCKING_SLEEP' if name == 'time.sleep' else None)
        if hot_path and code:
            self.issues.append({'code': code, 'file': self.filename, 'line': node.lineno,
                                'call': name, 'context': current, 'status': 'review_candidate',
                                'message': 'Verifique frequência, cache e fluxo real antes de corrigir.'})
        self.generic_visit(node)


def audit_source(text, filename='<string>'):
    try:
        tree = ast.parse(text, filename=filename)
    except SyntaxError as exc:
        return [{'code': 'SYNTAX_ERROR', 'file': filename, 'line': exc.lineno,
                 'status': 'parse_error', 'message': exc.msg}]
    scanner = Auditor(filename)
    scanner.visit(tree)
    return scanner.issues


def audit_project(root):
    root = Path(root).resolve()
    scope = root / 'src' if (root / 'src').is_dir() else root
    files = [scope] if scope.is_file() else sorted(scope.rglob('*.py'))
    results = []
    for path in files:
        if any(p in EXCLUDED for p in path.relative_to(root.parent if root.is_file() else root).parts):
            continue
        try:
            results.extend(audit_source(path.read_text(encoding='utf-8-sig'), str(path)))
        except (OSError, UnicodeError) as exc:
            results.append({'code': 'READ_ERROR', 'file': str(path), 'line': None,
                            'status': 'read_error', 'message': str(exc)})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--out', type=Path, help='JSON output; stdout if omitted')
    args = parser.parse_args()
    if not args.root.exists():
        parser.error('Root does not exist')
    findings = audit_project(args.root)
    report = {'root': str(args.root.resolve()), 'findings': findings,
              'limitations': ['Heuristic candidates are not confirmed bugs.',
                              'No proof of dt correctness, collision safety or full call-graph coverage.',
                              'FRect or scalar float positions do not require Vector2.']}
    data = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data + '\n', encoding='utf-8')
    else:
        print(data)
    return 2 if any(x['code'] in ('SYNTAX_ERROR', 'READ_ERROR') for x in findings) else 0


if __name__ == '__main__':
    raise SystemExit(main())
