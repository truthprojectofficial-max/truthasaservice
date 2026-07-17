// Order Get It Right -- Tauri shell library
//
// This is the entire Rust surface area of the desktop binary. It does
// four things and four things only:
//   1. Open the existing web front-end in a native WebView2 window.
//   2. Expose a tiny, auditable set of commands to the front-end.
//   3. Log every command invocation to a human-readable audit log.
//   4. Hash the current build to a `bin_id` so the audit trail can
//      record which exact binary produced a given result.
//
// All real audit logic lives in the Python runtime. The Rust shell
// is the wrapper, not the engine.

use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::Mutex;

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use tauri::Manager;

mod commands;

static AUDIT_LOG: Mutex<Option<PathBuf>> = Mutex::new(None);

/// Build identifier: SHA-256 of the executable itself, truncated.
/// Stored at first run and read by the front-end so the operator can
/// attach the exact binary to any incident report.
fn compute_bin_id(exe: &PathBuf) -> String {
    let bytes = fs::read(exe).unwrap_or_default();
    let mut hasher = Sha256::new();
    hasher.update(&bytes);
    let digest = hasher.finalize();
    hex::encode(&digest[..8])
}

fn log_audit_line(line: &str) {
    if let Ok(mut guard) = AUDIT_LOG.lock() {
        if let Some(path) = guard.as_ref() {
            if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(path) {
                let _ = writeln!(f, "{}", line);
            }
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct StartupInfo {
    pub project: String,
    pub version: String,
    pub bin_id: String,
    pub audit_log_path: String,
    pub python_runtime_path: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CommandLog {
    pub timestamp: String,
    pub command: String,
    pub args: serde_json::Value,
    pub result: String,
    pub bin_id: String,
}

#[tauri::command]
fn get_startup_info() -> StartupInfo {
    let exe = std::env::current_exe().unwrap_or_default();
    let bin_id = compute_bin_id(&exe);
    StartupInfo {
        project: "Order Get It Right".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        bin_id,
        audit_log_path: commands::audit_log_path_string(),
        python_runtime_path: commands::python_runtime_path_string(),
    }
}

#[tauri::command]
fn log_command(command: String, args: serde_json::Value, result: String) {
    let log = CommandLog {
        timestamp: chrono::Utc::now().to_rfc3339(),
        command,
        args,
        result,
        bin_id: get_startup_info().bin_id,
    };
    if let Ok(json) = serde_json::to_string(&log) {
        log_audit_line(&json);
    }
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            // Resolve the audit log path under the app's local data dir.
            let log_path = app
                .path()
                .app_local_data_dir()
                .unwrap_or_else(|_| std::env::temp_dir())
                .join("audit.log");
            if let Some(parent) = log_path.parent() {
                let _ = fs::create_dir_all(parent);
            }
            *AUDIT_LOG.lock().unwrap() = Some(log_path);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_startup_info, log_command])
        .run(tauri::generate_context!())
        .expect("error while running Order Get It Right desktop shell");
}
