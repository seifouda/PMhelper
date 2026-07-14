# Code Signing Guide — PMhelper Edu

> **Why:** An unsigned `.exe` from PyInstaller will be flagged by Windows Defender SmartScreen and many AV vendors. Code signing is the **single most effective** way to eliminate false positives.

---

## How Code Signing Reduces False Positives

Windows Defender uses **reputation-based trust**:

| Factor              | Unsigned     | Self-Signed | CA-Signed (EV) |
| ------------------- | ------------ | ----------- | -------------- |
| SmartScreen warning | Always       | Sometimes   | Never          |
| Defender block      | Often        | Rarely      | Never          |
| VirusTotal flags    | 5-15 vendors | 1-3 vendors | 0 vendors      |
| User trust          | Very low     | Medium      | High           |

**Authenticode** (Microsoft's signing standard) embeds a cryptographic signature in the `.exe`. Windows verifies this signature and attributes the file to a known publisher.

---

## Option 1: Self-Signed Certificate (Free, Internal Use)

Best for: Development, testing, distributing to students who trust you.

### Create the certificate (one-time)

```powershell
# Run as Administrator in PowerShell
$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject "CN=PMHelper Team, O=PMHelper, L=London, C=GB" `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(3)

# Export as PFX (password-protected)
$pwd = ConvertTo-SecureString -String "YourSecurePassword123!" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "pmhelper_codesign.pfx" -Password $pwd

Write-Host "Certificate thumbprint: $($cert.Thumbprint)"
```

### Sign the executable

```powershell
# Find signtool.exe (comes with Windows SDK)
$signtool = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" -Recurse |
    Sort-Object FullName -Descending | Select-Object -First 1

# Sign
& $signtool.FullName sign `
    /f "pmhelper_codesign.pfx" `
    /p "YourSecurePassword123!" `
    /fd SHA256 `
    /td SHA256 `
    /tr "http://timestamp.digicert.com" `
    /d "PMhelper Edu" `
    /du "https://github.com/seifouda/PMhelper" `
    "dist\PMhelper_Edu\PMhelper_Edu.exe"
```

### Verify the signature

```powershell
& $signtool.FullName verify /v /pa "dist\PMhelper_Edu\PMhelper_Edu.exe"
```

> **Limitation:** Self-signed certs don't build SmartScreen reputation. Users will still see "Unknown publisher" on first run, but the signature prevents AV quarantine.

---

## Option 2: Trusted CA Certificate (Paid, Public Release)

Best for: Public distribution to students, lecturers, universities.

### Recommended providers

| Provider         | Type                | Price (annual) | SmartScreen Trust                |
| ---------------- | ------------------- | -------------- | -------------------------------- |
| Sectigo / Comodo | OV Code Signing     | ~€120/yr       | Yes, after reputation builds     |
| DigiCert         | OV Code Signing     | ~€300/yr       | Yes, after reputation builds     |
| DigiCert         | **EV Code Signing** | ~€400/yr       | **Instant** (no reputation wait) |
| SSL.com          | OV Code Signing     | ~€200/yr       | Yes, after reputation builds     |

**EV (Extended Validation)** certificates provide **instant** SmartScreen trust — no waiting for reputation to build. This is the gold standard.

### Sign with a CA certificate

```powershell
# With PFX file from CA
& signtool.exe sign `
    /f "your_certificate.pfx" `
    /p "certificate_password" `
    /fd SHA256 `
    /td SHA256 `
    /tr "http://timestamp.digicert.com" `
    /d "PMhelper Edu" `
    /du "https://github.com/seifouda/PMhelper" `
    "dist\PMhelper_Edu\PMhelper_Edu.exe"

# Dual-sign (SHA1 + SHA256 for older Windows)
& signtool.exe sign `
    /f "your_certificate.pfx" `
    /p "certificate_password" `
    /fd SHA1 `
    /t "http://timestamp.digicert.com" `
    /d "PMhelper Edu" `
    "dist\PMhelper_Edu\PMhelper_Edu.exe"

& signtool.exe sign `
    /f "your_certificate.pfx" `
    /p "certificate_password" `
    /fd SHA256 `
    /td SHA256 `
    /tr "http://timestamp.digicert.com" `
    /as `
    /d "PMhelper Edu" `
    "dist\PMhelper_Edu\PMhelper_Edu.exe"
```

---

## Option 3: Azure Trusted Signing (Cloud-Based)

Microsoft's cloud signing service. Good for GitHub Actions CI/CD.

1. Create Azure account (free tier available)
2. Set up Trusted Signing resource in Azure portal
3. Use `azure-code-signing` GitHub Action in your CI pipeline

```yaml
# .github/workflows/build.yml (excerpt)
- name: Sign executable
  uses: azure/trusted-signing-action@v0.4.0
  with:
    azure-tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    azure-client-id: ${{ secrets.AZURE_CLIENT_ID }}
    azure-client-secret: ${{ secrets.AZURE_CLIENT_SECRET }}
    endpoint: https://eus.codesigning.azure.net/
    trusted-signing-account-name: pmhelper-signing
    certificate-profile-name: pmhelper-edu
    files-folder: dist/PMhelper_Edu
    files-folder-filter: exe
```

---

## Installing Windows SDK (for signtool.exe)

If `signtool.exe` is not found:

```powershell
# Check if already installed
Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" -ErrorAction SilentlyContinue

# If not found, install via winget (Windows 10+)
winget install Microsoft.WindowsSDK.10.0.22621

# Or download from:
# https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
```

---

## VirusTotal Submission Workflow

After building and optionally signing:

1. Go to [VirusTotal](https://www.virustotal.com/)
2. Upload `dist\PMhelper_Edu\PMhelper_Edu.exe`
3. Wait for scan (~2 minutes)
4. If any vendor flags it:
   - Note the vendor name and detection label
   - Most vendors have a false-positive report form
   - Submit to each flagging vendor

### Microsoft Defender False Positive Report

1. Go to: https://www.microsoft.com/en-us/wdsi/filesubmission
2. Sign in with Microsoft account
3. Select "Software developer" and "I believe this file is incorrectly detected"
4. Upload the `.exe`
5. Response time: usually 1-3 business days

### Common Vendor False-Positive Forms

| Vendor      | Submit URL                                                 |
| ----------- | ---------------------------------------------------------- |
| Microsoft   | https://www.microsoft.com/en-us/wdsi/filesubmission        |
| ESET        | https://support.eset.com/en/kb141                          |
| Kaspersky   | https://opentip.kaspersky.com/                             |
| Avast/AVG   | https://www.avast.com/false-positive-file-form.php         |
| Bitdefender | https://www.bitdefender.com/consumer/support/answer/29358/ |

---

## Quick Reference: Full Build + Sign Workflow

```powershell
# 1. Build (build scripts live in packaging/)
.\packaging\build_production.ps1

# 2. Sign (with self-signed cert — replace password/path as needed)
$signtool = (Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" -Recurse |
    Sort-Object FullName -Descending | Select-Object -First 1).FullName

& $signtool sign /f "pmhelper_codesign.pfx" /p "YourPassword" `
    /fd SHA256 /td SHA256 /tr "http://timestamp.digicert.com" `
    /d "PMhelper Edu" "dist\PMhelper_Edu\PMhelper_Edu.exe"

# 3. Verify
& $signtool verify /v /pa "dist\PMhelper_Edu\PMhelper_Edu.exe"

# 4. Submit to VirusTotal
Start-Process "https://www.virustotal.com/"
```
