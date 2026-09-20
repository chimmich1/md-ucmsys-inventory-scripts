# Keep native diagnostics intact when Windows PowerShell 5.1 callers use Stop
# and redirect all streams into Tee-Object. Fail only after the process exits.
function Invoke-NativeCommand {
  param(
    [Parameter(Mandatory=$true)][string]$Executable,
    [string[]]$Arguments = @()
  )
  $command = Get-Command -Name $Executable -CommandType Application -ErrorAction Stop
  $savedPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = "Continue"
    & $command.Source @Arguments 2>&1 | ForEach-Object { $_.ToString() }
    $nativeExitCode = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $savedPreference
  }
  if ($nativeExitCode -ne 0) {
    throw "Native command failed: $Executable (exit code $nativeExitCode)"
  }
}
