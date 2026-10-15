# Premier démarrage GED-ECM (Windows PowerShell)
$ProjectDir = "$PSScriptRoot\.."
$Created = $false
if (-not (Test-Path "$ProjectDir\.env")) { Copy-Item "$ProjectDir\.env.example" "$ProjectDir\.env"; $Created = $true }
if (-not (Test-Path "$ProjectDir\config\mayan.env")) { Copy-Item "$ProjectDir\config\mayan.env.example" "$ProjectDir\config\mayan.env" }
if ($Created) {
    Write-Host "Fichier .env créé : renseignez les mots de passe puis relancez scripts\init.ps1"
    exit 1
}
docker compose --project-directory $ProjectDir up -d
Write-Host "Mayan démarre (2 à 5 min au premier lancement) : http://localhost:8000"
Write-Host "Puis : python scripts\seed_meh.py --password <MAYAN_ADMIN_PASSWORD>"
