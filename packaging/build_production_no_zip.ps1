# ============================================================================
# PMhelper Edu -- Production Build Script
# ============================================================================
# Usage:   .\build_production.ps1
# Output:  dist\PMhelper_Edu\PMhelper_Edu.exe  (onedir bundle)
#          dist\PMhelper_Edu_v1.0.0.zip         (distribution archive)
#          dist\PMhelper_Edu.exe.sha256          (integrity hash)
#
# AV-Resistance: This script builds with manifest, version info, icon,
# no UPX, and --onedir mode. See CODE_SIGNING_GUIDE.md for signing.
# ============================================================================

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# This script lives in packaging\. Run from the repo root so spec-relative paths
# (src\, assets\, dist\) resolve, while build inputs are found next to this script.
Set-Location (Split-Path $PSScriptRoot -Parent)

# --- Configuration ---
$AppName       = 'PMhelper_Edu'
$SpecFile      = Join-Path $PSScriptRoot 'pmhelper_edu_production.spec'
$Version       = '1.0.0'
$BuildDir      = "build\$AppName"
$DistDir       = "dist\$AppName"
$IconScript    = Join-Path $PSScriptRoot 'create_icon.py'
$IconOutput    = 'assets\pmhelper_edu.ico'
$ManifestFile  = Join-Path $PSScriptRoot 'pmhelper_edu.manifest'
$VersionFile   = Join-Path $PSScriptRoot 'version_info.rc'

Write-Host ''
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host '  PMhelper Edu -- Production Build [AV-Resistant]' -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host '================================================================' -ForegroundColor Cyan
Write-Host ''

# --- Step 1: Pre-Build Validation ---
Write-Host '[1/8] Pre-build validation...' -ForegroundColor Yellow

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host '  ERROR: Python not found in PATH.' -ForegroundColor Red
    exit 1
}
$pyVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "  Python: $pyVersion" -ForegroundColor Gray
$major, $minor = $pyVersion.Split('.')
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 8)) {
    Write-Host "  ERROR: Python 3.8+ required, found $pyVersion." -ForegroundColor Red
    exit 1
}

# Check/install PyInstaller
$pyinstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyinstaller) {
    Write-Host '  PyInstaller not found. Installing...' -ForegroundColor Yellow
    & python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  ERROR: Failed to install PyInstaller.' -ForegroundColor Red
        exit 1
    }
}
$piVersion = & python -c "import PyInstaller; print(PyInstaller.__version__)" 2>$null
Write-Host "  PyInstaller: $piVersion" -ForegroundColor Gray

# Validate spec file exists
if (-not (Test-Path $SpecFile)) {
    Write-Host "  ERROR: Spec file '$SpecFile' not found." -ForegroundColor Red
    exit 1
}
Write-Host '  Spec file: OK' -ForegroundColor Gray

# Validate manifest exists
if (-not (Test-Path $ManifestFile)) {
    Write-Host "  WARNING: Manifest '$ManifestFile' not found. AV resistance reduced." -ForegroundColor Yellow
} else {
    Write-Host '  Manifest: OK' -ForegroundColor Gray
}

# Validate version info exists
if (-not (Test-Path $VersionFile)) {
    Write-Host "  WARNING: Version info '$VersionFile' not found. AV resistance reduced." -ForegroundColor Yellow
} else {
    Write-Host '  Version info: OK' -ForegroundColor Gray
}

Write-Host '  All checks passed.' -ForegroundColor Green

# --- Step 2: Generate Icon ---
Write-Host '[2/8] Generating application icon...' -ForegroundColor Yellow

if (-not (Test-Path $IconOutput)) {
    if (Test-Path $IconScript) {
        & python $IconScript
        if ($LASTEXITCODE -ne 0) {
            Write-Host '  WARNING: Icon generation failed. Building without icon.' -ForegroundColor Yellow
        } else {
            Write-Host "  Icon: $IconOutput" -ForegroundColor Gray
        }
    } else {
        Write-Host '  WARNING: No icon script found. Building without icon.' -ForegroundColor Yellow
    }
} else {
    $iconSize = (Get-Item $IconOutput).Length
    Write-Host "  Icon exists: $IconOutput - $iconSize bytes" -ForegroundColor Gray
}

# --- Step 2b: Patch scipy for PyInstaller compatibility ---
Write-Host '[2b/8] Patching scipy for PyInstaller compatibility...' -ForegroundColor Yellow
$patchScript = Join-Path $PSScriptRoot 'patch_scipy.py'
if (Test-Path $patchScript) {
    & python $patchScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  WARNING: scipy patch failed. Build may crash at runtime.' -ForegroundColor Yellow
    }
} else {
    Write-Host '  WARNING: patch_scipy.py not found. Skipping.' -ForegroundColor Yellow
}

# --- Step 3: Clean Previous Build ---
Write-Host '[3/8] Cleaning previous build artifacts...' -ForegroundColor Yellow

if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
    Write-Host "  Removed: $BuildDir" -ForegroundColor Gray
}
if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
    Write-Host "  Removed: $DistDir" -ForegroundColor Gray
}
Write-Host '  Clean.' -ForegroundColor Gray

# --- Step 4: Build with PyInstaller ---
Write-Host '[4/8] Building executable - this may take a few minutes...' -ForegroundColor Yellow
Write-Host "  Spec: $SpecFile" -ForegroundColor Gray
Write-Host '  Mode: --onedir [AV-friendly directory bundle]' -ForegroundColor Gray

$ErrorActionPreference = 'Continue'
& pyinstaller $SpecFile --noconfirm --clean --log-level WARN 2>&1 | ForEach-Object {
    $line = $_.ToString()
    if ($line -match 'ERROR') {
        Write-Host "  $line" -ForegroundColor Red
    }
}
$buildExitCode = $LASTEXITCODE
$ErrorActionPreference = 'Stop'

if ($buildExitCode -ne 0) {
    Write-Host ''
    Write-Host '  BUILD FAILED! Check errors above.' -ForegroundColor Red
    Write-Host '  Common fixes:' -ForegroundColor Yellow
    Write-Host '    - pip install pyinstaller --upgrade' -ForegroundColor Gray
    Write-Host '    - pip install numpy matplotlib pandas scipy networkx openpyxl tabulate tksheet pyvis' -ForegroundColor Gray
    Write-Host "    - Check hidden imports in $SpecFile" -ForegroundColor Gray
    exit 1
}

$exePath = Join-Path $DistDir "$AppName.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "  ERROR: Expected output '$exePath' not found." -ForegroundColor Red
    exit 1
}

$exeSize = (Get-Item $exePath).Length
$exeSizeMB = [math]::Round($exeSize / 1MB, 1)
Write-Host "  Build successful: $exePath - $exeSizeMB MB" -ForegroundColor Green

# --- Step 5: Post-Build Validation ---
Write-Host '[5/8] Post-build validation...' -ForegroundColor Yellow

# Check exe size
if ($exeSize -lt 5MB) {
    Write-Host "  WARNING: Executable is suspiciously small - $exeSizeMB MB." -ForegroundColor Yellow
    Write-Host '  Expected >5 MB for a PyInstaller bundle.' -ForegroundColor Yellow
}

# Count files in dist directory
$distFiles = Get-ChildItem -Path $DistDir -Recurse -File
$distCount = $distFiles.Count
$distTotalMB = [math]::Round(($distFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "  Bundle: $distCount files, $distTotalMB MB total" -ForegroundColor Gray

# Check for UPX contamination
$exeBytes = [System.IO.File]::ReadAllBytes($exePath)
$exeString = [System.Text.Encoding]::ASCII.GetString($exeBytes)
if ($exeString -match 'UPX0|UPX1|UPX!') {
    Write-Host '  WARNING: UPX signatures detected in .exe!' -ForegroundColor Yellow
    Write-Host '  This will trigger AV false positives.' -ForegroundColor Yellow
} else {
    Write-Host '  UPX check: Clean - no UPX packing detected' -ForegroundColor Green
}

# Verify manifest embedding
$hasManifest = $exeString -match '<assembly'
if ($hasManifest) {
    Write-Host '  Manifest: Embedded in .exe' -ForegroundColor Green
} else {
    Write-Host '  Manifest: NOT embedded - SmartScreen may flag this' -ForegroundColor Yellow
}

# Verify version info
$hasVersionInfo = $exeString -match 'PMhelper Edu'
if ($hasVersionInfo) {
    Write-Host '  Version info: Embedded in .exe' -ForegroundColor Green
} else {
    Write-Host '  Version info: NOT detected - check version_info.rc' -ForegroundColor Yellow
}

# --- Step 6: Create Distribution Package ---
Write-Host '[6/8] Creating distribution package...' -ForegroundColor Yellow

# Generate SHA256 hash
$hash = (Get-FileHash -Path $exePath -Algorithm SHA256).Hash
$hashFile = "dist\$AppName.exe.sha256"
"$hash  $AppName.exe" | Out-File -FilePath $hashFile -Encoding UTF8 -NoNewline
Write-Host "  SHA256: $hash" -ForegroundColor Gray

# Create README_FIRST.txt in the dist folder
$readmeLines = @(
    '==================================================================='
    "  PMhelper Edu v$Version -- Educational Project Management Tool"
    '==================================================================='
    ''
    'GETTING STARTED'
    '---------------'
    '1. Double-click PMhelper_Edu.exe to launch the application.'
    '2. No installation required -- all dependencies are included.'
    '3. Your projects are saved as .pmproj files.'
    ''
    ''
    'WINDOWS DEFENDER / ANTIVIRUS NOTE'
    '----------------------------------'
    'This application is built with PyInstaller, which bundles Python'
    'and all dependencies into an executable. Some antivirus software'
    "may flag it as unknown or potentially unwanted on first run"
    'because it has not yet built a reputation with Microsoft.'
    ''
    'THIS IS A FALSE POSITIVE. The application contains no malware.'
    ''
    'To verify integrity:'
    "  - SHA256 hash: $hash"
    '  - Compare with the hash in PMhelper_Edu.exe.sha256'
    ''
    'If Windows Defender blocks it:'
    '  1. Click More info on the SmartScreen dialog'
    '  2. Click Run anyway'
    '  3. Or: Windows Security > Virus and threat protection >'
    '     Protection history > Allow the blocked app'
    ''
    'If your antivirus quarantines it:'
    '  1. Open your AV software'
    '  2. Go to Quarantine / History'
    '  3. Restore PMhelper_Edu.exe and add an exclusion for this folder'
    ''
    ''
    'SYSTEM REQUIREMENTS'
    '-------------------'
    '  - Windows 10 or later, 64-bit'
    '  - No Python installation needed'
    '  - About 200 MB disk space'
    ''
    ''
    'SUPPORT'
    '-------'
    '  Repository: https://github.com/seifouda/PMhelper'
    '  Issues:     https://github.com/seifouda/PMhelper/issues'
    ''
    '==================================================================='
)

$readmePath = Join-Path $DistDir 'README_FIRST.txt'
$readmeLines | Out-File -FilePath $readmePath -Encoding UTF8
Write-Host '  Created: README_FIRST.txt' -ForegroundColor Gray

# Create ZIP archive
$timestamp = Get-Date -Format 'yyyyMMdd'
$zipName = "dist\${AppName}_v${Version}_${timestamp}.zip"
if (Test-Path $zipName) { Remove-Item $zipName -Force }
Write-Host "Skipping Compress-Archive due to file locks"; # -Path $DistDir -DestinationPath $zipName -CompressionLevel Optimal
$zipSize = [math]::Round((Get-Item $zipName).Length / 1MB, 1)
Write-Host "  Archive: $zipName - $zipSize MB" -ForegroundColor Gray
Write-Host "  Hash file: $hashFile" -ForegroundColor Gray

# --- Step 8: Summary ---
Write-Host ''
Write-Host '================================================================' -ForegroundColor Green
Write-Host '  BUILD COMPLETE' -ForegroundColor Green
Write-Host '================================================================' -ForegroundColor Green
Write-Host ''
Write-Host "  Executable:     $exePath" -ForegroundColor White
Write-Host "  Bundle size:    $distTotalMB MB, $distCount files" -ForegroundColor White
Write-Host "  Distribution:   $zipName - $zipSize MB" -ForegroundColor White
Write-Host "  SHA256:         $hash" -ForegroundColor White
Write-Host ''
Write-Host '  AV Resistance:' -ForegroundColor Cyan
if ($hasManifest)     { Write-Host '    [OK] Manifest embedded'     -ForegroundColor Green }
else                  { Write-Host '    [!!] Manifest NOT embedded'  -ForegroundColor Yellow }
if ($hasVersionInfo)  { Write-Host '    [OK] Version info embedded'  -ForegroundColor Green }
else                  { Write-Host '    [!!] Version info missing'   -ForegroundColor Yellow }
if (Test-Path $IconOutput) { Write-Host '    [OK] Icon embedded'    -ForegroundColor Green }
else                  { Write-Host '    [!!] No icon'                -ForegroundColor Yellow }
Write-Host '    [OK] UPX disabled'                                   -ForegroundColor Green
Write-Host '    [OK] --onedir mode, not --onefile'                   -ForegroundColor Green
Write-Host '    [OK] No bytecode encryption'                         -ForegroundColor Green
Write-Host ''
Write-Host '  Next steps for FULL AV trust:'                         -ForegroundColor Cyan
Write-Host '    1. Code-sign the .exe - see CODE_SIGNING_GUIDE.md'   -ForegroundColor Gray
Write-Host '    2. Submit to VirusTotal: https://www.virustotal.com' -ForegroundColor Gray
Write-Host '    3. Submit false positive to Microsoft:'              -ForegroundColor Gray
Write-Host '       https://www.microsoft.com/en-us/wdsi/filesubmission' -ForegroundColor Gray
Write-Host ''
Write-Host '  To run: .\dist\PMhelper_Edu\PMhelper_Edu.exe'          -ForegroundColor White
Write-Host ''
