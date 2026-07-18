# Tauri Windows Code-Signing Options for Order Get It Right

## Current state

- Tauri config: `02_Technical/tauri-shell/tauri.conf.json`
- Bundle targets: `msi`, `nsis`
- **No signing configured** (`bundle.windows.certificateThumbprint` missing).
- Build currently produces **unsigned** installer/executable.

## Why sign

Without a certificate, Windows Defender SmartScreen shows "Unknown publisher" and may block the installer. A signed binary:
- Shows your name as publisher in UAC.
- Reduces SmartScreen warnings over time as reputation builds.
- Required if you ever distribute the MSI to clients.

## Three practical routes

### Option A: Standard code-signing certificate (recommended)

Vendors: Sectigo, DigiCert, SSL.com, Certum, SignMyCode.

- **OV (Organization Validated)**: ~USD 216–400/year.
- **EV (Extended Validation)**: ~USD 280–560/year.
- Post-June 2023: OV requires a FIPS-compliant USB token or cloud HSM to store the private key; EV has always required one.

Steps:
1. Buy certificate. Provide business/identity docs; DUNS number helps.
2. Receive USB token or cloud HSM credentials.
3. Install certificate into Windows certificate store (`certmgr.msc` → Personal/Certificates).
4. Note `Thumbprint`, `digestAlgorithm` (usually sha256), and timestamp URL from vendor.
5. Add to `tauri.conf.json` under `bundle.windows`:

```json
"windows": {
  "certificateThumbprint": "A1B1A2B2...",
  "digestAlgorithm": "sha256",
  "timestampUrl": "http://timestamp.sectigo.com"
}
```

6. Run `tauri build`. Tauri calls `signtool.exe` automatically.

### Option B: Azure Trusted Signing (Azure Artifact Signing)

- Microsoft-native alternative.
- Pay per signature or monthly account fee.
- Requires Azure account, Entra ID app registration, and `artifact-signing-cli`.
- Good if you already use Azure; bad for independent-node air-gap goal.

Tauri config:

```json
"bundle": {
  "windows": {
    "signCommand": "artifact-signing-cli -e https://<region>.codesigning.azure.net -a MyAccount -c MyProfile -d 'Order Get It Right' %1"
  }
}
```

### Option C: Self-signed certificate (dev/test only)

- Free, but Windows still warns "Unknown publisher".
- Useful only for internal testing.
- Not a replacement for Option A or B.

## Cost summary

| Route | Upfront | Ongoing | Best for |
|---|---|---|---|
| Standard OV cert | USD 216–400 | ~same yearly | Independent-node, air-gap |
| EV cert | USD 280–560 | ~same yearly | Maximum trust, faster SmartScreen reputation |
| Azure Trusted Signing | minimal | per-signature / monthly | Existing Azure shop |
| Self-signed | free | free | Internal testing only |

## Recommendation for this project

Given the independent-node, air-gap, black-box-free design goal, **Option A (standard OV certificate on a USB token)** is the least disruptive. It keeps the signing key in your physical possession and requires no cloud dependency.

Do not sign until you are ready to distribute the MSI outside your own machines. Signing is a LOW-priority open item.
