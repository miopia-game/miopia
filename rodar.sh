#!/bin/sh
# Inicialização da pasta de desenvolvimento. O pacote offline contém o próprio Python.
set -eu
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
for candidato in "$base/.venv/bin/python" python3 python3.14 python3.13 python3.12 python3.11 python3.10; do
    if "$candidato" -c 'import sys; sys.exit(not ((3,10) <= sys.version_info[:2] <= (3,14)))' 2>/dev/null; then
        exec "$candidato" "$base/tools/preparar.py" "$@"
    fi
done
aviso="Para jogar offline, extraia o pacote de distribuição e abra Miopia. O atalho de desenvolvimento precisa de Python 3.10 a 3.14."
printf '%s\n' "$aviso" >&2
if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && command -v zenity >/dev/null; then
    zenity --error --title=Miopia --text="$aviso" || :
fi
exit 1
