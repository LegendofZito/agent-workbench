#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_home="${XDG_DATA_HOME:-${HOME}/.local/share}"
config_home="${XDG_CONFIG_HOME:-${HOME}/.config}"
launcher_home="${data_home}/agent-workbench/cli"
running_pid="$(
  pgrep -o -f "^(/usr/bin/)?python3 ${HOME}/.local/bin/agent-workbench$" \
    2>/dev/null || true
)"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'Missing Python 3. On Fedora, run: sudo dnf install python3 python3-tkinter xdg-utils\n' >&2
  exit 1
fi
if ! python3 -c 'import tkinter' >/dev/null 2>&1; then
  printf 'Missing Tkinter. On Fedora, run: sudo dnf install python3-tkinter xdg-utils\n' >&2
  exit 1
fi
if ! command -v xdg-open >/dev/null 2>&1; then
  printf 'Missing xdg-utils. On Fedora, run: sudo dnf install xdg-utils\n' >&2
  exit 1
fi
if ! python3 -c 'import PIL' >/dev/null 2>&1; then
  printf 'Optional image previews unavailable. On Fedora, run: sudo dnf install python3-pillow\n' >&2
fi
if ! python3 - <<'PY' >/dev/null 2>&1
import tkinter as tk
root = tk.Tcl()
root.eval("package require tkdnd")
PY
then
  printf 'Optional drag and drop unavailable. On Fedora, run: sudo dnf install tkdnd\n' >&2
fi

install -d "${HOME}/.local/bin" "${data_home}/applications" "${data_home}/icons"
install -d "${launcher_home}"
install -d "${config_home}/agent-workbench"
install -m 0755 "${root}/agent-workbench" \
  "${HOME}/.local/bin/agent-workbench"
ln -sfn agent-workbench "${HOME}/.local/bin/codex-conversation-viewer"
# Local-LLM delegation MCP server (free token-saving sub-agent over Ollama).
if [[ -f "${root}/local_delegate_server.py" ]]; then
  install -m 0644 "${root}/local_delegate_server.py" \
    "${config_home}/agent-workbench/local_delegate_server.py"
fi
install -m 0644 "${root}/agent-workbench.desktop" \
  "${data_home}/applications/agent-workbench.desktop"
rm -f "${data_home}/applications/codex-conversation-viewer.desktop"
install -m 0644 "${root}/assets/agent-workbench.png" \
  "${data_home}/icons/agent-workbench.png"
for launcher in claude codex gemini; do
  install -m 0755 "${root}/cli-launchers/${launcher}" \
    "${launcher_home}/${launcher}"
done
path_line='export PATH="${HOME}/.local/share/agent-workbench/cli:${PATH}"'
if [[ -f "${HOME}/.bashrc" ]] && ! grep -Fqx "${path_line}" "${HOME}/.bashrc"; then
  printf '\n%s\n' "${path_line}" >> "${HOME}/.bashrc"
fi
printf '{\n  "source_dir": "%s"\n}\n' "${root//\\/\\\\}" \
  > "${config_home}/agent-workbench/install.json"
if [[ -n "${running_pid}" ]]; then
  printf '{\n  "pid": %s\n}\n' "${running_pid}" \
    > "${config_home}/agent-workbench/update-request.json"
fi
rm -f "${data_home}/icons/codex-workbench.png"
command -v update-desktop-database >/dev/null 2>&1 \
  && update-desktop-database "${data_home}/applications" >/dev/null 2>&1 || true
printf 'Installed Agent Workbench.\n'
