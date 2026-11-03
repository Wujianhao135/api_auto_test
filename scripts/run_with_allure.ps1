# 一键运行测试并生成 Allure HTML 报告
# 用法：在项目根目录执行  powershell -File scripts/run_with_allure.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "====> 1. 运行测试，生成 Allure 结果..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m pytest tests/ --alluredir reports/allure-results --clean-alluredir -v
if ($LASTEXITCODE -ne 0) { Write-Host "测试失败，仍生成报告" -ForegroundColor Yellow }

Write-Host "====> 2. 生成 HTML 报告..." -ForegroundColor Cyan
$prefix = npm prefix -g
& "$prefix\allure.cmd" generate reports/allure-results -o reports/allure-report --clean

Write-Host "====> 完成！报告路径：reports\allure-report\index.html" -ForegroundColor Green
