# Sauvegarde GED-ECM : dump Postgres + rappel volume media
$ProjectDir = "$PSScriptRoot\.."
$Date = Get-Date -Format "yyyyMMdd-HHmm"
docker compose --project-directory $ProjectDir exec -T postgres pg_dump -U mayan mayan > "$ProjectDir\backup-$Date.sql"
Write-Host "Dump SQL : backup-$Date.sql"
Write-Host "Pensez a sauvegarder aussi le volume mayanmedia (Restic / copie volume) — voir docs/02-deploiement.md"
