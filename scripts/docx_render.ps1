<#
.SYNOPSIS
  Convert a .docx to PDF using Word itself, and report its page count.

.DESCRIPTION
  Word is the ground truth for .docx layout. LibreOffice's engine differs enough to
  mislead, so on Windows this is the renderer to trust; treat soffice output as a
  preview only.

  Prints "PAGES=<n>" to stdout. That number comes from ComputeStatistics(2)
  (wdStatisticPages) and is the cheapest possible "does it still fit on one page"
  check - run it on every build, before bothering to rasterize anything.

.NOTES
  Word COM requires absolute paths.

  Quit() runs in a finally block on purpose: an orphaned WINWORD.EXE keeps a file
  lock on the .docx, and the next build then fails for a reason that looks unrelated.

  DisplayAlerts = 0 suppresses the repair prompt, which means a corrupt document
  opens silently. A clean export plus a correct-looking render is therefore also the
  validity check - don't treat "it exported" alone as proof the file is sound.
#>
param(
  [Parameter(Mandatory = $true)][string]$Docx,
  [Parameter(Mandatory = $true)][string]$Pdf
)

$ErrorActionPreference = 'Stop'

$Docx = [System.IO.Path]::GetFullPath($Docx)
$Pdf = [System.IO.Path]::GetFullPath($Pdf)

if (-not (Test-Path -LiteralPath $Docx)) {
  Write-Error "No such docx: $Docx"
  exit 1
}

$outDir = Split-Path -Parent $Pdf
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) {
  New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}
# A stale PDF is as misleading as a stale PNG.
if (Test-Path -LiteralPath $Pdf) { Remove-Item -LiteralPath $Pdf -Force }

$word = $null
$doc = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0

  # ConfirmConversions = false, ReadOnly = true
  $doc = $word.Documents.Open($Docx, [ref]$false, [ref]$true)

  # 17 = wdExportFormatPDF, OpenAfterExport = false, 0 = wdExportOptimizeForPrint
  $doc.ExportAsFixedFormat($Pdf, 17, $false, 0)

  # 2 = wdStatisticPages
  $pages = $doc.ComputeStatistics(2)
  Write-Output ("PAGES=" + $pages)
}
finally {
  if ($doc) {
    try { $doc.Close([ref]$false) } catch { }
    try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null } catch { }
  }
  if ($word) {
    try { $word.Quit() } catch { }
    try { [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null } catch { }
  }
  [System.GC]::Collect()
  [System.GC]::WaitForPendingFinalizers()
}

if (-not (Test-Path -LiteralPath $Pdf)) {
  Write-Error "Word reported no error but produced no PDF: $Pdf"
  exit 1
}
Write-Output ("PDF=" + $Pdf)
