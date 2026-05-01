#Requires -Version 5.1
<#
Prepares this project for GitHub publication.

Default mode is safe: it initializes git if needed, checks ignored files,
stages public files, and shows what would be committed.

Examples:
  .\publish_to_github.ps1
  .\publish_to_github.ps1 -Commit
  .\publish_to_github.ps1 -RepoUrl "https://github.com/USER/REPO.git" -Commit -Push
#>

[CmdletBinding()]
param(
    [string]$RepoUrl = "",
    [string]$Branch = "main",
    [string]$CommitMessage = "Initial public version",
    [switch]$Commit,
    [switch]$Push
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    Write-Error $Message
    exit 1
}

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Fail "Required command '$Name' was not found. Install Git for Windows first: https://git-scm.com/download/win"
    }
}

function Assert-FileContainsNoExampleSecrets {
    $example = Join-Path $Root ".env.example"
    if (-not (Test-Path -LiteralPath $example)) {
        Fail ".env.example is missing."
    }

    $text = Get-Content -LiteralPath $example -Raw
    $badPatterns = @(
        "TELEGRAM_API_HASH=.+",
        "TELEGRAM_PHONE=\+?[0-9]{7,}",
        "TELEGRAM_DRY_RUN=0"
    )

    foreach ($pattern in $badPatterns) {
        if ($text -match $pattern) {
            Fail ".env.example appears to contain real Telegram values. Replace them with placeholders before publishing."
        }
    }
}

function Assert-StagedFilesArePublic {
    $staged = @(git diff --cached --name-only)
    $blocked = @()
    $suspicious = @()

    foreach ($file in $staged) {
        $normalized = $file -replace "\\", "/"
        if (
            $normalized -match "(^|/)\.env($|/)" -or
            $normalized -match "\.session($|-journal$|-)" -or
            $normalized -match "\.(db|sqlite|sqlite3|bak)$" -or
            $normalized -match "^(logs|qa_screenshots|venv|\.venv|__pycache__)/"
        ) {
            $blocked += $file
        }

        if ($normalized -match "\.(md|py|ps1|txt|example|json|yml|yaml)$") {
            $content = git show ":$file" 2>$null
            if ($LASTEXITCODE -eq 0 -and (
                ($content -match "Users[\\/][^\\/]+") -or
                ($content -match "Рабочий стол") -or
                ($content -match "TELEGRAM_PHONE=\+?[0-9]{7,}") -or
                ($content -match "TELEGRAM_API_HASH=.{8,}")
            )) {
                $suspicious += $file
            }
        }
    }

    if ($blocked.Count -gt 0) {
        Write-Host "Blocked files staged for commit:" -ForegroundColor Red
        $blocked | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Fail "Sensitive or generated files are staged. Unstage them before publishing."
    }

    if ($suspicious.Count -gt 0) {
        Write-Host "Files with possible personal data or secrets:" -ForegroundColor Red
        $suspicious | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Fail "Clean these files before publishing."
    }
}

Require-Command git

Write-Step "Checking public configuration"
Assert-FileContainsNoExampleSecrets

Write-Step "Initializing git repository if needed"
if (-not (Test-Path -LiteralPath (Join-Path $Root ".git"))) {
    git init | Write-Host
}

Write-Step "Configuring branch"
git branch -M $Branch

Write-Step "Staging files allowed by .gitignore"
git add .

Write-Step "Verifying staged files"
Assert-StagedFilesArePublic

Write-Host ""
Write-Host "Files staged for GitHub:" -ForegroundColor Green
git diff --cached --name-status

if (-not $Commit) {
    Write-Host ""
    Write-Host "Dry run complete. No commit or push was made." -ForegroundColor Yellow
    Write-Host "To commit locally: .\publish_to_github.ps1 -Commit"
    Write-Host "To commit and push: .\publish_to_github.ps1 -RepoUrl `"https://github.com/USER/REPO.git`" -Commit -Push"
    exit 0
}

Write-Step "Creating commit"
$hasChanges = git diff --cached --quiet; $diffExit = $LASTEXITCODE
if ($diffExit -eq 0) {
    Write-Host "Nothing staged to commit."
} else {
    git commit -m $CommitMessage
}

if (-not $Push) {
    Write-Host ""
    Write-Host "Commit step complete. No push was made." -ForegroundColor Yellow
    exit 0
}

if ([string]::IsNullOrWhiteSpace($RepoUrl)) {
    Fail "RepoUrl is required when using -Push."
}

Write-Host ""
Write-Host "This will upload the staged/committed public repository to:" -ForegroundColor Yellow
Write-Host "  $RepoUrl" -ForegroundColor Yellow
$confirmation = Read-Host "Type PUSH to continue"
if ($confirmation -ne "PUSH") {
    Fail "Push cancelled."
}

Write-Step "Configuring remote"
$remotes = @(git remote)
if ($remotes -contains "origin") {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

Write-Step "Pushing to GitHub"
git push -u origin $Branch

Write-Host ""
Write-Host "Published to GitHub." -ForegroundColor Green
