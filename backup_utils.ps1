<#
.SYNOPSIS
    Script robusto para gestión de backups de base de datos (Local y VPS).
.DESCRIPTION
    Permite generar dumps con timestamps, restaurar backups específicos y gestionar
    el ciclo de vida de los datos sin sobrescrituras accidentales.
.PARAMETER Action
    'backup-local', 'backup-vps', 'restore-local', 'restore-vps'
.PARAMETER Tag
    Etiqueta opcional para el nombre del archivo (ej: 'pre-update', 'recover').
.EXAMPLE
    .\backup_utils.ps1 -Action backup-local -Tag antes-de-scrape
    Genera: backups/local_20240113_1430_antes-de-scrape.dump
#>

param (
    [Parameter(Mandatory = $true)]
    [ValidateSet('backup-local', 'backup-vps', 'restore-local', 'restore-vps', 'upload-to-vps')]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [string]$Tag = "manual",

    [Parameter(Mandatory = $false)]
    [string]$FilePath
)

$ErrorActionPreference = "Stop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$BackupDir = "backups"

# Crear directorio de backups si no existe
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

function Get-BackupName {
    param ($Source)
    return "$BackupDir\${Source}_${Timestamp}_${Tag}.dump"
}

try {
    switch ($Action) {
        'backup-local' {
            $TargetFile = Get-BackupName "local"
            Write-Host "[INFO] Creating LOCAL backup at: $TargetFile" -ForegroundColor Cyan
            docker exec -i local_postgres_dump pg_dump -U admin -Fc realestate_db > $TargetFile
            if ($LASTEXITCODE -eq 0) { Write-Host "[SUCCESS] Backup created." -ForegroundColor Green }
        }

        'backup-vps' {
            $TargetFile = Get-BackupName "vps"
            Write-Host "[INFO] Downloading VPS backup to: $TargetFile" -ForegroundColor Cyan
            # Remote dump -> Pipe -> Local file
            ssh vps-scraping "docker exec webscrapinginmobiliaria-db-1 pg_dump -U admin -Fc realestate_db" > $TargetFile
            if ($LASTEXITCODE -eq 0) { Write-Host "[SUCCESS] Remote backup downloaded." -ForegroundColor Green }
        }

        'upload-to-vps' {
            if (-not $FilePath) { throw "Must specify -FilePath for upload." }
            if (-not (Test-Path $FilePath)) { throw "File not found: $FilePath" }
            
            Write-Host "[INFO] Uploading $FilePath to VPS..." -ForegroundColor Cyan
            $RemotePath = "/tmp/" + (Split-Path $FilePath -Leaf)
            scp $FilePath "vps-scraping:${RemotePath}"
            
            Write-Host "[INFO] Copying to container..."
            ssh vps-scraping "docker cp ${RemotePath} webscrapinginmobiliaria-db-1:${RemotePath}"
            
            Write-Host "[SUCCESS] File ready on VPS at: $RemotePath" -ForegroundColor Green
        }

        'restore-local' {
            if (-not $FilePath) { throw "Must specify -FilePath for restore." }
            Write-Host "[WARN] RESTORING to LOCAL from: $FilePath" -ForegroundColor Yellow
            
            if ($FilePath.EndsWith(".sql")) {
                Get-Content $FilePath | docker exec -i local_postgres_dump psql -U admin -d realestate_db
            }
            else {
                # Assume Custom Format (-Fc)
                Get-Content $FilePath -Encoding Byte | docker exec -i local_postgres_dump pg_restore -U admin -d realestate_db --clean --if-exists
            }
            Write-Host "[SUCCESS] Restore completed." -ForegroundColor Green
        }
    }
}
catch {
    Write-Error "[ERROR] $_"
}
