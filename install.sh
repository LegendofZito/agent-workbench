#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_home="${XDG_DATA_HOME:-${HOME}/.local/share}"
config_home="${XDG_CONFIG_HOME:-${HOME}/.config}"

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
install -d "${config_home}/agent-workbench"
install -m 0755 "${root}/agent-workbench" \
  "${HOME}/.local/bin/agent-workbench"
ln -sfn agent-workbench "${HOME}/.local/bin/codex-conversation-viewer"
install -m 0644 "${root}/agent-workbench.desktop" \
  "${data_home}/applications/agent-workbench.desktop"
rm -f "${data_home}/applications/codex-conversation-viewer.desktop"
install -m 0644 "${root}/assets/agent-workbench.png" \
  "${data_home}/icons/agent-workbench.png"
printf '{\n  "source_dir": "%s"\n}\n' "${root//\\/\\\\}" \
  > "${config_home}/agent-workbench/install.json"
rm -f "${data_home}/icons/codex-workbench.png"
command -v update-desktop-database >/dev/null 2>&1 \
  && update-desktop-database "${data_home}/applications" >/dev/null 2>&1 || true
printf 'Installed Agent Workbench.\n'
