# Premier démarrage GED-ECM
Copy-Item -Path "$PSScriptRoot\..\.env.example" -Destination "$PSScriptRoot\..\.env" -ErrorAction SilentlyContinue
Copy-Item -Path "$PSScriptRoot\..\config\mayan.env.example" -Destination "$PSScriptRoot\..\config\mayan.env" -ErrorAction SilentlyContinue
Write-Host "Renseignez les mots de passe dans .env puis : docker compose up -d"
docker compose --project-directory "$PSScriptRoot\.." up -d
docker compose --project-directory "$PSScriptRoot\.." logs -f app
