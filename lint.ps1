Write-Host "`n Running isort..." -ForegroundColor Cyan
isort .

Write-Host "`n Running black..." -ForegroundColor Cyan
black .

Write-Host "`n Running flake8..." -ForegroundColor Cyan
flake8 .

Write-Host "`n Done!" -ForegroundColor Green
