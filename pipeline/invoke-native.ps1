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

function Get-GitCommitSha {
  param([Parameter(Mandatory=$true)][string]$Repository)
  if (!(Test-Path (Join-Path $Repository ".git"))) { return "UNKNOWN" }
  try {
    # Capture all output and the native exit code before inspecting the result.
    # Piping to Select-Object -First 1 terminates git early on PowerShell 5.1 and
    # can change LASTEXITCODE to -1 even though the SHA was emitted.
    $output = @(& git -C $Repository rev-parse HEAD 2>$null)
    $nativeExitCode = $LASTEXITCODE
    if ($nativeExitCode -eq 0 -and $output.Count -gt 0) {
      $candidate = [string]$output[0]
      if ($candidate -match '^[0-9a-fA-F]{40}$') { return $candidate.ToLowerInvariant() }
    }
  } catch {}
  return "UNKNOWN"
}
