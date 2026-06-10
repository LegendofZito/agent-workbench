#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_home="${XDG_DATA_HOME:-${HOME}/.local/share}"
install -d "${HOME}/.local/bin" "${data_home}/applications" "${data_home}/icons"
install -m 0755 "${root}/codex-conversation-viewer" \
  "${HOME}/.local/bin/codex-conversation-viewer"
install -m 0644 "${root}/codex-conversation-viewer.desktop" \
  "${data_home}/applications/codex-conversation-viewer.desktop"
install -m 0644 "${root}/assets/codex-workbench.png" \
  "${data_home}/icons/codex-workbench.png"
command -v update-desktop-database >/dev/null 2>&1 \
  && update-desktop-database "${data_home}/applications" >/dev/null 2>&1 || true
printf 'Installed Codex Conversation Viewer.\n'
