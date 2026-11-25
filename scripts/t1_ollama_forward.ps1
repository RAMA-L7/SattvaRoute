param(
  [Parameter(Mandatory=$true)][string]$BodyFile,
  [Parameter(Mandatory=$true)][string]$OutFile,
  [string]$Endpoint = 'http://127.0.0.1:11434/v1/chat/completions',
  [int]$TimeoutSec = 120
)
$ErrorActionPreference = 'Stop'
$body = Get-Content -LiteralPath $BodyFile -Raw
$result = @{ status = 0; body = '' }
try {
  $resp = Invoke-WebRequest -Uri $Endpoint -Method Post -Body $body -ContentType 'application/json' -TimeoutSec $TimeoutSec -UseBasicParsing
  $result.status = [int]$resp.StatusCode
  $result.body = $resp.Content
} catch {
  $result.status = 502
  $safe = ($_.Exception.Message -replace '["\\]', ' ')
  $result.body = '{"error":"transport_failed","detail":"' + $safe.Substring(0, [Math]::Min(180, $safe.Length)) + '"}'
}
$result | ConvertTo-Json -Compress -Depth 3 | Set-Content -LiteralPath $OutFile -Encoding UTF8
