$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$candidates = @()

# 1) Bundled Python (dev machine only; skipped elsewhere)
$bundled = Join-Path $env:USERPROFILE ".dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if (Test-Path -LiteralPath $bundled) {
    $candidates += @{ Exe = $bundled; Args = @() }
}

# 2) Python Launcher
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    $candidates += @{ Exe = $py.Source; Args = @("-3") }
}

# 3) python on PATH (skip the Windows Store placeholder)
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python -and $python.Source -notmatch "WindowsApps") {
    $candidates += @{ Exe = $python.Source; Args = @() }
}

foreach ($c in $candidates) {
    $checkArgs = @($c.Args) + @("-c", "import sys; sys.exit(0 if sys.version_info[0] == 3 else 1)")
    & $c.Exe @checkArgs 2>$null
    if ($LASTEXITCODE -eq 0) {
        $runArgs = @($c.Args) + @("server.py")
        if ($env:WHUOJ_NO_OPEN -ne "1") { $runArgs += "--open" }
        $runArgs += $args
        & $c.Exe @runArgs
        if ($LASTEXITCODE -ne 0) { Read-Host "Press Enter to exit" }
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "Python 3 was not found."
Write-Host "Please install Python 3.10+ and enable 'Add Python to PATH'."
Write-Host "https://www.python.org/downloads/"
Write-Host ""
Read-Host "Press Enter to exit"
exit 1
