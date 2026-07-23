//! Order Get It Right -- OAuth 2.0 PKCE handler (Google)
//!
//! Per the operator's architectural research at
//!   .hermes/plans/OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt
//!
//! Implements Google OAuth 2.0 with PKCE on a local loopback listener.
//! Uses the NARROW `drive.file` scope (NOT full drive) so we bypass
//! Google's 100-user brand verification audit.
//!
//! Flow:
//!   1. Bind a TcpListener on 127.0.0.1:0 (any free port)
//!   2. Generate a PKCE code_verifier + code_challenge
//!   3. Open the user's browser to Google's authorization endpoint
//!   4. Block on a tiny HTTP server that catches the redirect
//!   5. Extract the auth code from the redirect query string
//!   6. Return the code to the WebView2 frontend
//!
//! The frontend then POSTs the code to Google's token endpoint to
//! exchange it for access_token + refresh_token.

use std::io::{Read, Write};
use std::net::TcpListener;
use std::time::Duration;
use base64::{Engine as _, engine::general_purpose::URL_SAFE_NO_PAD};
use sha2::{Sha256, Digest};

/// The Google OAuth client ID. Operator must set this in the Tauri config
/// after registering the OAuth client at console.cloud.google.com.
const GOOGLE_AUTH_URL: &str = "https://accounts.google.com/o/oauth2/v2/auth";
const GOOGLE_TOKEN_URL: &str = "https://oauth2.googleapis.com/token";

/// The drive.file scope. NARROW. No full drive. Bypasses Google's audit.
const SCOPE: &str = "https://www.googleapis.com/auth/drive.file openid email profile";

/// PKCE code_verifier: random URL-safe string, 43-128 chars
fn generate_code_verifier() -> String {
    // 32 random bytes -> 43 base64-url chars (no padding)
    use rand::RngCore;
    let mut bytes = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut bytes);
    URL_SAFE_NO_PAD.encode(bytes)
}

/// PKCE code_challenge: SHA-256 of code_verifier, base64-url encoded
fn generate_code_challenge(verifier: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(verifier.as_bytes());
    let digest = hasher.finalize();
    URL_SAFE_NO_PAD.encode(digest)
}

/// Run the Google OAuth handshake.
///
/// Returns (auth_code, redirect_uri) on success.
/// The frontend then POSTs to GOOGLE_TOKEN_URL to exchange.
#[tauri::command]
pub fn google_handshake() -> Result<(String, String), String> {
    // 1. Bind a local loopback listener on any free port
    let listener = TcpListener::bind("127.0.0.1:0")
        .map_err(|e| format!("port binding failed: {e}"))?;
    let port = listener.local_addr()
        .map_err(|e| format!("local_addr failed: {e}"))?
        .port();
    let redirect_uri = format!("http://127.0.0.1:{port}");

    // 2. Generate PKCE values
    let verifier = generate_code_verifier();
    let challenge = generate_code_challenge(&verifier);

    // 3. Build the authorization URL
    //    The Operator's research uses drive.file scope, prompt=consent for offline access
    let auth_url = format!(
        "{GOOGLE_AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={redirect_uri}\
         &response_type=code&scope={SCOPE}&code_challenge={challenge}\
         &code_challenge_method=S256&access_type=offline&prompt=consent",
    );

    // 4. Open the user's browser. The Operator is on Windows; use `start`.
    #[cfg(target_os = "windows")]
    {
        std::process::Command::new("cmd")
            .args(&["/C", "start", &auth_url])
            .spawn()
            .map_err(|e| format!("failed to open browser: {e}"))?;
    }

    // 5. Block on the loopback listener for the callback
    listener.set_read_timeout(Some(Duration::from_secs(120)))
        .map_err(|e| format!("set_read_timeout failed: {e}"))?;

    let (mut stream, _) = listener.accept()
        .map_err(|e| format!("listener.accept failed: {e}"))?;

    // 6. Read the HTTP request
    let mut buf = [0u8; 4096];
    let n = stream.read(&mut buf)
        .map_err(|e| format!("read failed: {e}"))?;
    let request = String::from_utf8_lossy(&buf[..n]).to_string();

    // 7. Extract the auth code from the GET request
    let auth_code = extract_code(&request)
        .ok_or_else(|| "auth code not found in callback".to_string())?;

    // 8. Send a friendly HTML response to the browser
    let response = "HTTP/1.1 200 OK\r\n\
                    Content-Type: text/html\r\n\r\n\
                    <html><body>\
                    <h4>Sign-in complete. You can close this tab and return to the application.</h4>\
                    </body></html>";
    stream.write_all(response.as_bytes())
        .map_err(|e| format!("write failed: {e}"))?;

    Ok((auth_code, redirect_uri))
}

/// Extract the `code` query parameter from a GET request.
fn extract_code(request: &str) -> Option<String> {
    let first_line = request.lines().next()?;
    // GET /?code=XXXXX&scope=... HTTP/1.1
    let path_and_query = first_line.split_whitespace().nth(1)?;
    let query = path_and_query.split('?').nth(1)?;
    for pair in query.split('&') {
        let mut kv = pair.splitn(2, '=');
        if let (Some(k), Some(v)) = (kv.next(), kv.next()) {
            if k == "code" {
                return Some(url_decode(v));
            }
        }
    }
    None
}

/// URL-decode a percent-encoded string. Minimal implementation.
fn url_decode(s: &str) -> String {
    let mut out = Vec::with_capacity(s.len());
    let bytes = s.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        if bytes[i] == b'%' && i + 2 < bytes.len() {
            if let Ok(b) = u8::from_str_radix(
                std::str::from_utf8(&bytes[i+1..i+3]).unwrap_or("00"),
                16,
            ) {
                out.push(b);
                i += 3;
                continue;
            }
        } else if bytes[i] == b'+' {
            out.push(b' ');
            i += 1;
            continue;
        }
        out.push(bytes[i]);
        i += 1;
    }
    String::from_utf8_lossy(&out).to_string()
}

// Operator must set this in tauri.conf.json or env var after registering
// the OAuth client at console.cloud.google.com.
const CLIENT_ID: &str = "OPERATOR_SET_IN_TAURI_CONFIG";
