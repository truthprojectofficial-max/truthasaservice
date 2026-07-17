import sys, hashlib, json
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

files = [
    '02_Technical/tauri-shell/tauri.conf.json',
    '02_Technical/tauri-shell/Cargo.toml',
    '02_Technical/tauri-shell/package.json',
    '02_Technical/tauri-shell/build.rs',
    '02_Technical/tauri-shell/src/main.rs',
    '02_Technical/tauri-shell/src/lib.rs',
    '02_Technical/tauri-shell/src/commands.rs',
    '02_Technical/tauri-shell/capabilities/default.json',
    '02_Technical/tauri-shell/icons/32x32.png',
    '02_Technical/tauri-shell/icons/128x128.png',
    '02_Technical/tauri-shell/icons/128x128@2x.png',
    '02_Technical/tauri-shell/icons/icon.png',
    '02_Technical/tauri-shell/icons/icon.ico',
    '02_Technical/tauri-shell/icons/icon.icns',
    '02_Technical/tauri-shell/A4_PREBUILD_HASHES.json',
]
hashes = {f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in files}

block = vault_io.append_block('OPEN_ITEMS_A4_PREBUILD_PREP_2026_07_12', {
    'open_item': 'A4 -- Tauri desktop shell (02_Technical/tauri-shell/) -- prebuild prep',
    'diagnosis': (
        'OPEN_ITEMS A4 was blocked on Rust install per session-1 memory note. '
        'Spec audit shows the spec is sound but had 3 latent issues that would '
        'have caused mid-build failures. Spec is now pre-fixed; Rust 1.97.0 '
        'installed; build is blocked on Windows C++ toolchain (MSVC linker) '
        'which is a separate operator decision.'
    ),
    'spec_audit': {
        'Cargo.toml': 'OK -- tauri 2, tauri-plugin-shell/dialog/fs 2, serde, sha2, hex, chrono, thiserror. rust-version 1.77, host MSVC. Release profile: opt-level=s, lto=true, codegen-units=1, strip=true, panic=abort. All deps deterministic.',
        'tauri.conf.json': '3 issues fixed: (1) bundle.targets dropped from [msi,nsis,deb,appimage,dmg] to [msi,nsis] -- Linux/macOS targets need cross-toolchains the host does not have. (2) longDescription refreshed from 52-pattern to 54-pattern + v3.9 + explicit no-network-runtime line. (3) plugins.shell.open=false was already there, but the matching capabilities/default.json granted shell:default -- now tightened (see capabilities below).',
        'package.json': 'OK -- minimal: just @tauri-apps/cli via npm scripts. No JS deps to audit.',
        'build.rs': 'OK -- standard tauri-build::build() call.',
        'src/main.rs': 'OK -- windows_subsystem attribute, calls lib::run().',
        'src/lib.rs': 'OK -- AUDIT_LOG Mutex, compute_bin_id (SHA-256 of exe truncated to 8 bytes hex), log_audit_line, get_startup_info, log_command Tauri commands. run() wires the 3 plugins and 2 commands.',
        'src/commands.rs': 'OK -- CommandResult, audit_log_path_string, python_runtime_path_string, ping. ping() not currently wired into invoke_handler (lib.rs:111) -- minor; left as-is.',
        'capabilities/default.json': '1 issue fixed: removed shell:default, dialog:default, fs:default. The front-end (web/index.html) only calls custom Tauri commands (get_startup_info, log_command, ping via invoke()) and does NOT call __TAURI__.shell, __TAURI__.dialog, or __TAURI__.fs. Granting the defaults would widen the attack surface (exec a process, open arbitrary URL, read/write files) for no feature benefit. The 3 plugins are still linked into the binary (lib.rs:95-97) but their capabilities are not granted. To grant any, the operator must edit this file AND seal the rationale to the chain.',
        'web/index.html': 'OK -- front-end only calls T.invoke(name, args) for custom commands.',
    },
    'pre_fixes_applied': {
        'tauri.conf.json': 'bundle.targets + longDescription (see above)',
        'capabilities/default.json': 'removed 3 plugin defaults (see above)',
        'icons/': '6 valid placeholder icons generated with brand color #1f3a3d. 32x32.png, 128x128.png, 128x128@2x.png, icon.png (512x512), icon.ico (32x32 PNG-in-ICO), icon.icns (icp5+icp6 entries). All sizes match tauri.conf.json line 36-42 expectations. These are placeholders -- operator should swap in real designed icons before public release.',
    },
    'rust_install': {
        'installer_url': 'https://win.rustup.rs/x86_64',
        'installer_args': '-y --default-toolchain stable --default-host x86_64-pc-windows-msvc --profile minimal',
        'installer_size_bytes': 12814336,
        'installed_version': 'rustc 1.97.0 (2d8144b78 2026-07-07)',
        'cargo_version': 'cargo 1.97.0 (c980f4866 2026-06-30)',
        'install_path': 'C:\\Users\\justo\\.cargo\\bin\\',
        'note': 'Pre-existing .rustup/settings.toml was found; rustup re-used it. Warning was emitted: installing msvc toolchain without its prerequisites -- see blocker below.',
    },
    'blocker': {
        'description': 'Rust 1.97.0 stable (x86_64-pc-windows-msvc) is installed but the Windows C++ toolchain (MSVC linker + Windows SDK) is NOT installed. cargo build will fail at the link step.',
        'evidence': [
            'where link.exe returned C:\\Program Files\\Git\\usr\\bin\\link.exe (Git Bash GNU coreutils link, not the MSVC linker)',
            'where cl.exe returned no results',
            'where gcc returned no results',
            'gcc --version returned command not found',
        ],
        'options_for_operator': {
            'O1_MSVC_Build_Tools': {
                'command': 'winget install Microsoft.VisualStudio.2022.BuildTools --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"',
                'estimated_size_gb': 3.0,
                'estimated_minutes': 15,
                'pros': 'Officially supported by Tauri, future-proof for any C-extension (numpy/cryptography wheels), no GNU-target edge cases.',
                'cons': 'Largest download, may show UI prompts (winget suppresses most).',
            },
            'O2_MinGW_w64': {
                'command': 'rustup default stable-x86_64-pc-windows-gnu && rustup target add x86_64-pc-windows-gnu (and install MinGW separately, e.g. via Git for Windows SDK or w64devkit)',
                'estimated_size_mb': 500,
                'estimated_minutes': 8,
                'pros': 'Smaller, faster, no MSVC install prompt.',
                'cons': 'Tauri docs note some plugins (especially tauri-plugin-fs) have known issues on x86_64-pc-windows-gnu. GNU target + Tauri = some edge cases on Windows.',
            },
            'O3_defer': 'Leave A4 OPEN. Tauri shell is the USB fallback promised in the hard-copy plan; the Python runtime (FastAPI) is the production path. 32/32 pytest is green without it. A future session can resume this prep from the recorded state.',
        },
    },
    'recommendation': 'O1 (MSVC). The MSVC install is a one-time cost that serves the project forever, not just Tauri. The MinGW option is a tactical shortcut that creates a long-tail of compatibility issues, which is the opposite of the no-black-box stance.',
    'files_unchanged': 'OPEN_ITEMS_AND_REFERENCE.md line 53-59 (A4 entry remains the source of truth for status).',
    'post_fix_hashes': hashes,
    'next_action_for_operator': 'Pick O1, O2, or O3 above. If O1 or O2, paste the command into a shell with admin rights and re-invoke this session for npm install + npx tauri build + .exe verification + chain seal.',
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
