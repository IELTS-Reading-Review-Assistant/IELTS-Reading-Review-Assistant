$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (!(Test-Path '.venv\Scripts\python.exe')) { python -m venv .venv }
& '.\.venv\Scripts\python.exe' install_dependencies.py
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
New-Item -ItemType Directory -Force data,third_party | Out-Null
if (!(Test-Path 'data\ecdict.csv')) {
    Invoke-WebRequest 'https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv' -OutFile 'data\ecdict.csv'
}
Invoke-WebRequest 'https://raw.githubusercontent.com/skywind3000/ECDICT/master/LICENSE' -OutFile 'third_party\ECDICT-LICENSE.txt'
& '.\.venv\Scripts\python.exe' prepare_dictionary.py
if ($LASTEXITCODE -ne 0) { throw 'Dictionary import failed.' }
