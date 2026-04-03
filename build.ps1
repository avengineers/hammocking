<#
.DESCRIPTION
    Wrapper for installing dependencies, running and testing the project
#>

param(
    [switch]$clean ## clean build, wipe out all build artifacts
    , [switch]$install ## install mandatory packages
)

function Invoke-CommandLine {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute('PSAvoidUsingInvokeExpression', '', Justification = 'Usually this statement must be avoided (https://learn.microsoft.com/en-us/powershell/scripting/learn/deep-dives/avoid-using-invoke-expression?view=powershell-7.3), here it is OK as it does not execute unknown code.')]
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$CommandLine,
        [Parameter(Mandatory = $false, Position = 1)]
        [bool]$StopAtError = $true,
        [Parameter(Mandatory = $false, Position = 2)]
        [bool]$PrintCommand = $true,
        [Parameter(Mandatory = $false, Position = 3)]
        [bool]$Silent = $false
    )
    if ($PrintCommand) {
        Write-Output "Executing: $CommandLine"
    }
    $global:LASTEXITCODE = 0
    if ($Silent) {
        # Omit information stream (6) and stdout (1)
        Invoke-Expression $CommandLine 6>&1 | Out-Null
    }
    else {
        Invoke-Expression $CommandLine
    }
    if ($global:LASTEXITCODE -ne 0) {
        if ($StopAtError) {
            Write-Error "Command line call `"$CommandLine`" failed with exit code $global:LASTEXITCODE"
        }
        else {
            Write-Output "Command line call `"$CommandLine`" failed with exit code $global:LASTEXITCODE, continuing ..."
        }
    }
}

function Initialize-EnvPath {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Invoke-Setup {
    # Install scoop if not available
    if (-Not (Get-Command "scoop" -ErrorAction SilentlyContinue)) {
        Write-Output "Installing Scoop..."
        Invoke-CommandLine "powershell -ExecutionPolicy ByPass -c `"irm https://get.scoop.sh | iex`""
        Initialize-EnvPath
    }
    Write-Output "scoop version: $(scoop --version)"
    # Install uv if not available
    if (-Not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
        Write-Output "Installing uv..."
        Invoke-CommandLine "powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
        Initialize-EnvPath
    }
    Write-Output "uv version: $(uv --version)"
    # Create venv and install dependencies
    Invoke-CommandLine "uv sync"
}

function Remove-Path {
    param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$path
    )
    if (Test-Path -Path $path -PathType Container) {
        Write-Output "Deleting directory '$path' ..."
        Remove-Item $path -Force -Recurse
    }
    elseif (Test-Path -Path $path -PathType Leaf) {
        Write-Output "Deleting file '$path' ..."
        Remove-Item $path -Force
    }
}

## start of script
# Always set the $InformationPreference variable to "Continue" globally,
# this way it gets printed on execution and continues execution afterwards.
$InformationPreference = "Continue"

# Stop on first error
$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
Write-Output "Running in ${pwd}"

try {
    if ($clean) {
        Remove-Path ".venv"
    }

    # setup environment
    Invoke-Setup

    if (-Not $install) {
        if ($clean) {
            Remove-Path "build"
            Remove-Path "out"
        }
        # Run pypeline
        Invoke-CommandLine "uv run pypeline run"
    }
}
finally {
    Pop-Location
}
## end of script
