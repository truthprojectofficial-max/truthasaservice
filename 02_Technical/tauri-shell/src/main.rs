// Order Get It Right -- Tauri desktop entry point
// The Rust shell is intentionally thin. It opens the existing web UI
// (02_Technical/web/index.html) in a native WebView2 window and exposes
// a small set of auditable commands to the front-end.
//
// The Tauri shell has the same level of control as the operator. The
// web front-end calls `ogir_invoke` which routes through this module.
// Every command is keyed in src-tauri/src/commands.rs and recorded in
// the human-readable audit log at 04_Validation/tauri-audit.log.

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

fn main() {
    order_get_it_right_lib::run();
}
