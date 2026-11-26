#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
qa_profile=$(mktemp -d "${TMPDIR:-/tmp}/miopia-qa.XXXXXX")
trap 'rm -rf -- "$qa_profile"' EXIT HUP INT TERM
export MIOPIA_DADOS="$qa_profile"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
if [ -x .venv/bin/python ]; then
    qa_python=.venv/bin/python
else
    qa_python=python3
fi
exec_status=0
"$qa_python" -B -m pytest -q "$@" || exec_status=$?
exit "$exec_status"
