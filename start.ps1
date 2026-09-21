param(
    [string]$Gaeld = '0',
    [string]$Laan = '2000',
    [string]$Start = '2026-09',
    [string]$Slut = '2029-06',
    [string]$RenteEfter = '2,85',
    [ValidateSet(1,2)][int]$Interval = 2,
    [string]$Netto,
    [string]$Udgifter
)
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) { $runner = $pythonCommand.Source }
elseif (Test-Path -LiteralPath $bundledPython) { $runner = $bundledPython }
else { throw 'Python blev ikke fundet. Installer Python 3.10 eller nyere.' }
$budgetArgs = @()
if ($PSBoundParameters.ContainsKey('Netto')) { $budgetArgs += @('--netto', $Netto) }
if ($PSBoundParameters.ContainsKey('Udgifter')) { $budgetArgs += @('--udgifter', $Udgifter) }
& $runner -X utf8 (Join-Path $PSScriptRoot 'su_beregner.py') --gaeld $Gaeld --laan $Laan --start $Start --slut $Slut --rente-efter $RenteEfter --interval $Interval @budgetArgs
exit $LASTEXITCODE
