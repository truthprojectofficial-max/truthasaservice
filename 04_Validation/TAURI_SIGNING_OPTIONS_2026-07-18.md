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
| Standard OV certificate | USD 216–400 | ~same yearly | Independent-node, air-gap |
| EV certificate | USD 280–560 | ~same yearly | Immediate SmartScreen reputation; faster trust |
| Azure Trusted Signing | minimal | per-signature / monthly | Existing Azure users |
| Self-signed | free | free | Internal testing only |

## Important post-June 2023 change

This guide (and the source guide in `TAURI SIGNNG GUIDE.txt`) only applies to **OV certificates acquired before 1 June 2023**. Since that date, new OV certificates require a FIPS-compliant USB token or cloud HSM to store the private key; EV certificates have always required this. If you are buying a new certificate today, follow your issuer's current HSM/token instructions, not the older PFX-import steps.

## OV vs EV practical difference

- **EV certificate**: immediate Microsoft SmartScreen reputation. No download warning. Recommended if you are distributing to non-technical clients.
- **OV certificate**: cheaper and available to individuals, but SmartScreen will still warn users until the certificate builds reputation. You can submit the signed binary to Microsoft for manual review, which may remove the warning for that specific file.

## Recommendation for this project (revised)

If the app will be installed by clients who are not technical operators, **EV certificate** is worth the extra cost because it eliminates the SmartScreen friction immediately. If the app stays inside your own controlled environment or with technically capable operators who understand how to bypass a one-time SmartScreen warning, **OV + manual Microsoft review per release** is the cheaper independent-node option.

The independent-node architecture is preserved either way because the private key stays on a token you control; the only cloud touch is the optional Microsoft manual-review upload.

## Do not use self-signed for distribution

Self-signed certificates do not provide SmartScreen reputation and will show an unknown-publisher warning. Use them for internal testing only.
