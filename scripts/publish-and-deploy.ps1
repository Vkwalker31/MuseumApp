# Публикация образа на Docker Hub и деплой на Render
# Запуск: .\scripts\publish-and-deploy.ps1 -DockerHubUser ВАШ_ЛОГИН

param(
    [Parameter(Mandatory = $true)]
    [string]$DockerHubUser,

    [string]$ImageName = "museumapp",
    [string]$Tag = "latest"
)

$ErrorActionPreference = "Stop"
$full = "$DockerHubUser/${ImageName}:$Tag"

Write-Host "==> Проверка Docker..." -ForegroundColor Cyan
docker info | Out-Null

Write-Host "==> Логин в Docker Hub (откроется запрос пароля/токена)..." -ForegroundColor Cyan
Write-Host "Создайте Access Token: https://hub.docker.com/settings/security" -ForegroundColor Yellow
docker login -u $DockerHubUser
if ($LASTEXITCODE -ne 0) { throw "docker login failed" }

Write-Host "==> Сборка образа $full ..." -ForegroundColor Cyan
docker build -t $full .
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }

Write-Host "==> Push $full (публичный репозиторий)..." -ForegroundColor Cyan
docker push $full
if ($LASTEXITCODE -ne 0) { throw "docker push failed" }

Write-Host ""
Write-Host "OK: образ опубликован: https://hub.docker.com/r/$DockerHubUser/$ImageName" -ForegroundColor Green
Write-Host "Преподаватель: docker pull $full" -ForegroundColor Green
Write-Host ""
Write-Host "Дальше — деплой на Render (см. DEPLOY.md раздел Render from Docker Hub)" -ForegroundColor Cyan
Write-Host "Образ: $full"
