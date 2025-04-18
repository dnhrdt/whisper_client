#!/usr/bin/env pwsh
<#
.SYNOPSIS
    WhisperClient Linting Script
.DESCRIPTION
    Runs linting tools for WhisperClient code
.PARAMETER isort
    Run isort for import sorting
.PARAMETER black
    Run black for code formatting
.PARAMETER flake8
    Run flake8 for style checking
.PARAMETER mypy
    Run mypy for type checking
.PARAMETER pylint
    Run pylint for comprehensive code analysis
.PARAMETER all
    Run all linting tools
.PARAMETER files
    Target files or directories for linting (default: "src main.py")
.PARAMETER fix
    Enable fix mode for tools that support automatic fixes
.NOTES
    Version: 1.0
    Timestamp: 2025-03-09 01:50 CET
#>

param (
    [switch]$isort,
    [switch]$black,
    [switch]$flake8,
    [switch]$mypy,
    [switch]$pylint,
    [switch]$all,
    [string]$files = "src main.py",
    [switch]$fix
)

# Color definitions for output
$colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
}

# If no specific tools specified, run all
if (-not ($isort -or $black -or $flake8 -or $mypy -or $pylint -or $all)) {
    $all = $true
}

# If --all specified, enable all tools
if ($all) {
    $isort = $true
    $black = $true
    $flake8 = $true
    $mypy = $true
    $pylint = $true
}

# Parse target files
$targets = $files.Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)

# Function to run a linting tool
function Invoke-LintingTool {
    param (
        [string]$Name,
        [string]$Command,
        [string[]]$Arguments,
        [string]$Description,
        [bool]$CanFix = $false
    )

    Write-Host "`n[$Name] $Description" -ForegroundColor $colors.Header

    # Add fix parameter if possible and requested
    if ($fix -and $CanFix) {
        if ($Name -eq "isort") {
            # Note: --apply is deprecated, but isort applies changes by default when no check mode is specified
        }
        # black applies changes by default, no need for additional parameters
    }

    # Run tool and capture output
    $output = & $Command $Arguments $targets 2>&1
    $exitCode = $LASTEXITCODE

    # Display output
    $output | ForEach-Object {
        Write-Host $_
    }

    # Set status based on exit code
    if ($exitCode -eq 0) {
        Write-Host "$Name completed successfully." -ForegroundColor $colors.Success
    } else {
        $errorCount = ($output | Measure-Object).Count

        if ($Name -in @("isort", "black") -and $fix) {
            Write-Host "Changes applied by $Name." -ForegroundColor $colors.Warning
        } else {
            Write-Host "Warning: $Name found $errorCount issues." -ForegroundColor $colors.Warning
        }
    }
}

# Display header
Write-Host "===== WhisperClient Linting Process =====" -ForegroundColor $colors.Header
Write-Host "Target files: $files" -ForegroundColor $colors.Info
if ($fix) {
    Write-Host "Fix mode: Enabled" -ForegroundColor $colors.Warning
}

# 1. isort - Import sorting
if ($isort) {
    Invoke-LintingTool -Name "isort" -Command "python" -Arguments @("-m", "isort") -Description "Import sorting" -CanFix $true
}

# 2. black - Code formatting
if ($black) {
    # Invoke-LintingTool -Name "black" -Command "python" -Arguments @("-m", "black") -Description "Code formatting" -CanFix $true # Temporarily disabled
    Write-Host "`n[black] Code formatting temporarily disabled" -ForegroundColor $colors.Warning
}

# 3. flake8 - Style checking
if ($flake8) {
    Invoke-LintingTool -Name "flake8" -Command "python" -Arguments @("-m", "flake8") -Description "Style checking"
}

# 4. mypy - Type checking
if ($mypy) {
    Invoke-LintingTool -Name "mypy" -Command "python" -Arguments @("-m", "mypy") -Description "Type checking"
}

# 5. pylint - Comprehensive code analysis
if ($pylint) {
    Invoke-LintingTool -Name "pylint" -Command "python" -Arguments @("-m", "pylint") -Description "Comprehensive code analysis"
}

Write-Host "`n===== Linting Process Completed =====" -ForegroundColor $colors.Header
