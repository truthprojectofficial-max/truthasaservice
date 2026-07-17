import sys, hashlib, json
sys.path.insert(0, r'02_Technical')
from src.io import vault_io

pre = vault_io.merkle_stats()
print('PRE  root:', pre['merkleRoot'])
print('PRE count:', pre['blockCount'])

# Hash the three build outputs
outputs = {
    'raw_exe': '02_Technical/tauri-shell/target/release/order-get-it-right.exe',
    'msi': '02_Technical/tauri-shell/target/release/bundle/msi/Order Get It Right_1.0.0_x64_en-US.msi',
    'nsis': '02_Technical/tauri-shell/target/release/bundle/nsis/Order Get It Right_1.0.0_x64-setup.exe',
}
output_hashes = {}
for k, f in outputs.items():
    sz = __import__('os').path.getsize(f)
    sha = hashlib.sha256(open(f, 'rb').read()).hexdigest()
    output_hashes[k] = {'path': f, 'sha256': sha, 'bytes': sz}
    print(f'{k}: {sz} bytes, {sha}')

# Post-build source hashes (after 3 pre-fixes + 1 mid-build fix + 1 dev dep add)
source_files = [
    '02_Technical/tauri-shell/tauri.conf.json',
    '02_Technical/tauri-shell/Cargo.toml',
    '02_Technical/tauri-shell/package.json',
    '02_Technical/tauri-shell/build.rs',
    '02_Technical/tauri-shell/src/main.rs',
    '02_Technical/tauri-shell/src/lib.rs',
    '02_Technical/tauri-shell/src/commands.rs',
    '02_Technical/tauri-shell/capabilities/default.json',
    '02_Technical/tauri-shell/A4_PREBUILD_HASHES.json',
    '02_Technical/tauri-shell/A4_SEAL_PREBUILD.py',
]
source_hashes = {f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in source_files}

block = vault_io.append_block('OPEN_ITEMS_A4_CLOSED_2026_07_12', {
    'open_item': 'A4 -- Tauri desktop shell built and verified.',
    'toolchain_installed': {
        'rust': 'rustc 1.97.0 (2d8144b78 2026-07-07)',
        'cargo': 'cargo 1.97.0 (c980f4866 2026-06-30)',
        'rust_install_via': 'rustup-init.exe from https://win.rustup.rs/x86_64 (12.8 MB)',
        'msvc': 'Visual Studio Build Tools 2022 v17.14.35 (cl.exe + link.exe via vcvars64.bat at C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat)',
        'msvc_install_via': 'winget install --id Microsoft.VisualStudio.2022.BuildTools -e --force --accept-source-agreements --accept-package-agreements --disable-interactivity --override "--quiet --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"',
        'msvc_install_time_minutes': 14,
        'msvc_installed_components': 'MSVC v143, Windows 10/11 SDK (selected by --includeRecommended)',
        'wix': 'WiX Toolset v3.14.1 (downloaded by tauri-build for MSI bundle)',
        'nsis': 'NSIS v3.11 (downloaded by tauri-build for NSIS installer)',
    },
    'pre_fixes_applied': [
        'tauri.conf.json: bundle.targets trimmed from [msi,nsis,deb,appimage,dmg] to [msi,nsis]',
        'tauri.conf.json: longDescription refreshed from 52-pattern to 54-pattern + v3.9 + no-network-runtime line',
        'tauri.conf.json: removed "resources": ["resources/*"] -- the directory does not exist and Tauri build fails on glob mismatch',
        'capabilities/default.json: removed shell:default, dialog:default, fs:default -- front-end never uses those plugins, no-network principle',
        'package.json: added devDependencies: {"@tauri-apps/cli": "^2"} -- tauri command was referenced in scripts but not declared as a dep',
    ],
    'icons_generated': '6 valid placeholder files (brand color #1f3a3d): 32x32.png, 128x128.png, 128x128@2x.png, icon.png (512x512), icon.ico, icon.icns. Operator should swap in real designed icons before public release.',
    'build_outputs': output_hashes,
    'build_time_seconds': 110,  # 1m 50s on the final attempt (crates were warm from the first attempt)
    'build_warnings': [
        'variable does not need to be mutable (src/lib.rs:39) -- minor, the mut is on a Mutex guard pattern that is correct',
        'struct CommandResult is never constructed (src/commands.rs:16) -- ping() is defined but not registered in invoke_handler (lib.rs:111); left as-is to keep the change minimal',
        'function ping is never used -- same as above',
    ],
    'verification': {
        'launch_test': 'order-get-it-right.exe started, ran for 8+ seconds without crashing, MainWindowTitle = "Order Get It Right - Truth as a Service" (matches tauri.conf.json line 15). Process killed cleanly via Stop-Process. The .exe is a Windows GUI binary and cannot be headlessly verified further in this environment; the next operator must run it interactively to confirm the WebView2 window opens and renders the web UI.',
        'process_id_at_capture': 7488,
        'start_time_local': '2026-07-12T14:25:47+10:00',
    },
    'post_build_verification': {
        'pytest': '32/32 passed',
        'no_network_audit': 'CLEAN, exit 0',
        'verify_chain': 'MATCH',
    },
    'post_build_source_hashes': source_hashes,
    'files_unchanged': 'OPEN_ITEMS_AND_REFERENCE.md line 53-59 (the doc entry will be updated in a future C-series doc maintenance pass when the operator confirms the .exe works interactively).',
    'operator_action_required': [
        'Run order-get-it-right.exe from File Explorer or a fresh shell -- confirm the WebView2 window opens, the shell-tag in the top-right reads "shell: Tauri (desktop binary)" (not "shell: Browser (HTTP API)"), and the audit pipeline responds to clicks.',
        'Run "Order Get It Right_1.0.0_x64-setup.exe" (the NSIS installer) to confirm the install wizard works end-to-end on this host.',
        'Replace the 6 placeholder icons in 02_Technical/tauri-shell/icons/ with real designed icons before any public release.',
        'Address the 3 compiler warnings in a follow-up commit: register ping() in invoke_handler (lib.rs:111) and remove the spurious mut on the Mutex guard (lib.rs:39).',
    ],
})
print('SEAL block:', block['index'])
print('POST root:', block['current_hash'])
post = vault_io.merkle_stats()
print('POST count:', post['blockCount'])
