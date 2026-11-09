#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
runtime_root="${XDG_CACHE_HOME:-${HOME}/.cache}/codex-runtimes/codex-primary-runtime/dependencies"
runtime_node="${RUNTIME_NODE:-${runtime_root}/node/bin/node}"

if [[ -x "${script_dir}/../.venv/bin/python" ]] && \
  "${script_dir}/../.venv/bin/python" -c "import yaml" >/dev/null 2>&1; then
  export YAML_PYTHON="${YAML_PYTHON:-${script_dir}/../.venv/bin/python}"
fi

if [[ ! -x "${runtime_node}" ]]; then
  runtime_node="$(command -v node)"
fi

exec "${runtime_node}" "${script_dir}/generate_sesa_presentation.mjs" "$@"
