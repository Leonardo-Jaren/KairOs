#Requires -Version 5.1
<#
.SYNOPSIS
  Crea rama (si aplica), push, PR e issue de historia de usuario en GitHub Projects.

.EXAMPLE
  .\scripts\create-pr-and-project.ps1 -Descripcion "listar-equipos" -Modulo equipos -HistoriaTitulo "Listar equipos del laboratorio"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Descripcion,

    [Parameter(Mandatory = $true)]
    [string]$Modulo,

    [Parameter(Mandatory = $true)]
    [string]$HistoriaTitulo,

    [string]$AuthorInitials = "",
    [string]$BaseBranch = "",
    [switch]$SkipBranchCreation,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Write-Step($Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Read-JsonFile($Path) {
    if (-not (Test-Path $Path)) { return $null }
    return Get-Content $Path -Raw | ConvertFrom-Json
}

function Get-BranchSlug($Description) {
    $slug = $Description.ToLower()
    $slug = $slug -replace '\s+', '-'
    $slug = $slug -replace '[^a-z0-9\-]', ''
    $slug = $slug -replace '-{2,}', '-'
    return $slug.Trim('-')
}

function Get-AuthorInitials($Provided) {
    if ($Provided) { return $Provided.ToUpper() }

    $devConfig = Read-JsonFile (Join-Path $RepoRoot ".github/developer-config.json")
    if ($devConfig -and $devConfig.authorInitials) {
        return $devConfig.authorInitials.ToUpper()
    }

    throw "Define iniciales en -AuthorInitials o en .github/developer-config.json (copia developer-config.example.json)."
}

function Get-BranchName($Initials, $Slug) {
    $now = Get-Date
    $month = $now.ToString("MMM", [System.Globalization.CultureInfo]::InvariantCulture)
    $day = $now.Day
    $year = $now.Year
    return "{0}{1}_{2}{3}_{4}" -f $year, $Initials, $month, $day, $Slug
}

function Get-ChangeSummary {
    $base = if ($script:BaseBranch) { $script:BaseBranch } else { "main" }
    $summary = @()

    try {
        $log = git -C $RepoRoot log "$base..HEAD" --pretty=format:"- %s" 2>$null
        if ($log) { $summary += $log }
    } catch {}

    try {
        $stat = git -C $RepoRoot diff "$base...HEAD" --stat 2>$null
        if ($stat) {
            $summary += ""
            $summary += "### Archivos modificados"
            $summary += "``````"
            $summary += ($stat -join "`n")
            $summary += "``````"
        }
    } catch {}

    if (-not $summary) {
        $summary = "- Cambios incluidos en la rama actual."
    }

    return ($summary -join "`n")
}

function Build-IssueBody($Modulo, $HistoriaTitulo, $PrUrl) {
    $summary = Get-ChangeSummary
    $fecha = Get-Date -Format "yyyy-MM-dd"

    return @"
## Historia

**Como** usuario del sistema KairOs
**Quiero** $HistoriaTitulo
**Para** gestionar correctamente el modulo $Modulo

## Modulo

$Modulo

## Resumen de implementacion

$summary

## Documentacion

- RF: ``docs/requerimientos-funcionales/$Modulo-*.md``
- RNF: ``docs/requerimientos-no-funcionales/$Modulo-*.md``
- HU: ``docs/historias-de-usuario/$Modulo-*.md``

## Pull Request

$PrUrl

## Fecha

$fecha
"@
}

Push-Location $RepoRoot

try {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) no esta instalado. Instala desde https://cli.github.com/"
    }

    $projectConfig = Read-JsonFile (Join-Path $RepoRoot ".github/project-config.json")
    if (-not $projectConfig) {
        $projectConfig = Read-JsonFile (Join-Path $RepoRoot ".github/project-config.example.json")
        Write-Warning "Usando project-config.example.json. Copia a project-config.json y configura projectNumber."
    }

    if ($BaseBranch) {
        $script:BaseBranch = $BaseBranch
    } elseif ($projectConfig.baseBranch) {
        $script:BaseBranch = $projectConfig.baseBranch
    } else {
        $script:BaseBranch = "main"
    }

    $initials = Get-AuthorInitials $AuthorInitials
    $slug = Get-BranchSlug $Descripcion
    $branchName = Get-BranchName $initials $slug
    $prTitle = $HistoriaTitulo

    $currentBranch = git rev-parse --abbrev-ref HEAD

    if (-not $SkipBranchCreation -and $currentBranch -eq $script:BaseBranch) {
        Write-Step "Creando rama $branchName"
        if (-not $DryRun) {
            git checkout -b $branchName
            $currentBranch = $branchName
        }
    } else {
        Write-Step "Usando rama actual: $currentBranch"
    }

    $status = git status --porcelain
    if ($status) {
        throw "Hay cambios sin commitear. Haz commit antes de ejecutar este script."
    }

    Write-Step "Publicando rama $currentBranch"
    if (-not $DryRun) {
        git push -u origin $currentBranch
    }

    Write-Step "Creando pull request"
    $prBodyFile = New-TemporaryFile
    @"
## Descripcion

$HistoriaTitulo

Modulo: **$Modulo**

Generado con ``scripts/create-pr-and-project.ps1``.

## Checklist

- [ ] Capas y shared/ respetados
- [ ] Documentacion en docs/ actualizada
"@ | Set-Content -Path $prBodyFile -Encoding UTF8

    if ($DryRun) {
        Write-Host "[DryRun] gh pr create --base $($script:BaseBranch) --head $currentBranch --title `"$prTitle`""
        $prUrl = "https://github.com/OWNER/REPO/pull/DRY-RUN"
    } else {
        $prUrl = gh pr create --base $script:BaseBranch --head $currentBranch --title $prTitle --body-file $prBodyFile
    }
    Remove-Item $prBodyFile -ErrorAction SilentlyContinue

    Write-Host "PR: $prUrl" -ForegroundColor Green

    Write-Step "Creando issue (historia de usuario)"
    $issueBodyFile = New-TemporaryFile
    Build-IssueBody $Modulo $HistoriaTitulo $prUrl | Set-Content -Path $issueBodyFile -Encoding UTF8

    $labelArgs = @()
    if ($projectConfig.issueLabels) {
        foreach ($label in $projectConfig.issueLabels) {
            $labelArgs += "--label"
            $labelArgs += $label
        }
    }

    if ($DryRun) {
        Write-Host "[DryRun] gh issue create --title `"HU: $HistoriaTitulo`""
        $issueUrl = "https://github.com/OWNER/REPO/issues/DRY-RUN"
    } else {
        $issueArgs = @(
            "issue", "create",
            "--title", "HU: $HistoriaTitulo",
            "--body-file", $issueBodyFile
        ) + $labelArgs
        $issueUrl = & gh @issueArgs
    }
    Remove-Item $issueBodyFile -ErrorAction SilentlyContinue

    Write-Host "Issue: $issueUrl" -ForegroundColor Green

    if ($projectConfig.projectNumber) {
        Write-Step "Agregando issue al GitHub Project #$($projectConfig.projectNumber)"
        $owner = $projectConfig.owner
        if (-not $DryRun) {
            gh project item-add $projectConfig.projectNumber --owner $owner --url $issueUrl
        } else {
            Write-Host "[DryRun] gh project item-add $($projectConfig.projectNumber) --owner $owner --url $issueUrl"
        }
    } else {
        Write-Warning "projectNumber no configurado. Edita .github/project-config.json para vincular al Project."
    }

    Write-Step "Listo"
} finally {
    Pop-Location
}
