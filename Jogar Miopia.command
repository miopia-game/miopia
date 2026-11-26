#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"
export MIOPIA_DADOS="${MIOPIA_DADOS:-$PWD/.perfil-revisao}"
exec ./rodar.sh "$@"
