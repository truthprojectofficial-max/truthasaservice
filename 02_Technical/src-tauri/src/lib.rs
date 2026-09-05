// OrderGetItRight -- Tauri v2 entry point
//
// Per the operator's architectural research at
//   .hermes/plans/OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt
// (lines 262-271 specify the Tauri dependency block; 6 deps + "all" features)
//
// This lib.rs:
//   1. Registers the 5 research plugins: updater, dialog, process, store, http
//   2. Exposes 5 Tauri commands: audit_text, list_models, system_check, google_handshake, supabase_config
//   3. Subprocess invokes the Python engines (no network modules in Rust)

use std::process::Command;

#[derive(serde::Serialize)]
struct SupabaseConfig {
    configured: bool,
    url: String,
    #[serde(rename = "anonKey")]
    anon_key: String,
    #[serde(rename = "projectRef")]
    project_ref: String,
    #[serde(rename = "missingEnv")]
    missing_env: Vec<String>,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        // The 5 research plugins. Order matters: log last (so it captures
        // any setup errors from the others).
        .plugin(tauri_plugin_updater::Builder::new().build())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_http::init())
        // All 4 Tauri commands, including the OAuth PKCE handshake
        .invoke_handler(tauri::generate_handler![
            audit_text,
            list_models,
            system_check,
            supabase_config,
            commands::google_handshake
        ])
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

/// Run the lie-detector audit on the supplied text.
///
/// Wraps the Python audit_text() in src/engines/deception_scanner.py via
/// subprocess. Returns the JSON-serialised DeceptionReport.
///
/// The Tauri command takes the user's selected text and the
/// optional context, invokes Python (Python 3.14 on this host),
/// parses the JSON output, and returns it to the WebView2 frontend.
#[tauri::command]
fn audit_text(text: String, context: Option<String>) -> Result<String, String> {
    let python = r"C:\Python314\python.exe";
    let script = r"02_Technical\src\engines\deception_scanner.py";

    let mut cmd = Command::new(python);
    cmd.arg("-m")
        .arg("src.engines.deception_scanner")
        .arg("--input")
        .arg(&text);
    if let Some(ctx) = &context {
        cmd.arg("--context").arg(ctx);
    }
    cmd.arg("--json-only");

    let output = cmd
        .output()
        .map_err(|e| format!("failed to spawn python: {e}"))?;

    if !output.status.success() {
        return Err(format!(
            "audit failed: {}",
            String::from_utf8_lossy(&output.stderr)
        ));
    }
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

/// List the Ollama models available on the local stack (127.0.0.1:11434).
///
/// Used by the frontend to show a model picker. Loopback-only; no
/// network modules are imported in this Rust file (per the 5-allow-list
/// drop, 2026-07-24).
#[tauri::command]
fn list_models() -> Result<String, String> {
    let output = Command::new("curl")
        .arg("-s")
        .arg("http://127.0.0.1:11434/api/tags")
        .output()
        .map_err(|e| format!("failed to spawn curl: {e}"))?;
    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

/// Run the 12-system check and return a JSON verdict.
///
/// Returns 1 if any of the 12 systems is down. The operator can
/// then decide which action to take. Loopback-only; no external calls.
#[tauri::command]
fn system_check() -> Result<i32, String> {
    let output = Command::new("python")
        .arg("04_Validation/scripts/twelve_system_check.py")
        .output()
        .map_err(|e| format!("failed to spawn twelve_system_check: {e}"))?;
    Ok(output.status.code().unwrap_or(-1))
}

/// Return the Supabase shell configuration for the Tauri frontend.
///
/// The deterministic audit runtime remains local-only; this command only
/// exposes the shell-layer project URL + anon key so the desktop UI can
/// authenticate the current user and persist scan metadata to Supabase.
#[tauri::command]
fn supabase_config() -> SupabaseConfig {
    let url = std::env::var("OGIR_SUPABASE_URL").unwrap_or_default();
    let anon_key = std::env::var("OGIR_SUPABASE_ANON_KEY").unwrap_or_default();
    let mut missing_env = Vec::new();
    if url.is_empty() {
        missing_env.push("OGIR_SUPABASE_URL".to_string());
    }
    if anon_key.is_empty() {
        missing_env.push("OGIR_SUPABASE_ANON_KEY".to_string());
    }
    let project_ref = url
        .strip_prefix("https://")
        .or_else(|| url.strip_prefix("http://"))
        .unwrap_or(url.as_str())
        .split('.')
        .next()
        .unwrap_or("")
        .to_string();
    SupabaseConfig {
        configured: missing_env.is_empty(),
        url,
        anon_key,
        project_ref,
        missing_env,
    }
}

/// The OAuth PKCE commands module. Re-exported so generate_handler! can see it.
mod commands;
