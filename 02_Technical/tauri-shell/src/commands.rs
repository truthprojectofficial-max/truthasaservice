// Order Get It Right -- Tauri command surface
//
// This module exposes the only commands the front-end can call. Every
// command:
//   - returns a CommandResult with deterministic fields
//   - records itself in the audit log
//   - requires the operator to be explicit about what the action is
//
// No command here reaches out to a network. The Tauri runtime is
// network-disabled by the bundle policy in tauri.conf.json.

use std::path::PathBuf;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CommandResult {
    pub ok: bool,
    pub code: String,
    pub message: String,
}

pub fn audit_log_path_string() -> String {
    "audit.log (under app local data dir)".to_string()
}

pub fn python_runtime_path_string() -> String {
    // The Python interpreter is co-located with the executable.
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            return parent.join("python").join("python.exe").to_string_lossy().to_string();
        }
    }
    "python".to_string()
}

// NOTE: a previous revision defined a `ping` Tauri command here. It
// was never registered in `lib.rs`'s invoke_handler! macro, so the
// command was unreachable from the front-end. Removed as part of
// F15 (cleanup seal) -- dead code.
