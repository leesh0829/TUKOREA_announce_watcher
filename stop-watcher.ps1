param()

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\\Scripts\\python.exe"
$Controller = Join-Path $ProjectRoot "watcher_ctl.py"

if (-not (Test-Path $Python)) {
    throw "Python launcher not found: $Python"
}

& $Python $Controller stop
