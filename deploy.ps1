# 📦 Daily AI Digest — 一键部署脚本
# 在你自己电脑的终端里运行（需要已安装 git 和 GitHub CLI）

param(
    [string]$RepoName = "daily-ai-digest"
)

Write-Host "🚀 开始部署 AI 日报项目..." -ForegroundColor Cyan

# 1. 初始化仓库
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git 仓库已初始化" -ForegroundColor Green
} else {
    Write-Host "⏭️  Git 仓库已存在" -ForegroundColor Yellow
}

# 2. 添加文件
git add -A
git commit -m "🎉 初始化 AI 日报项目" --allow-empty

# 3. 检查 gh CLI
$hasGh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $hasGh) {
    Write-Host "⚠️  未安装 GitHub CLI (gh)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "手动操作步骤：" -ForegroundColor White
    Write-Host "  1. 打开 https://github.com/new" -ForegroundColor White
    Write-Host "    仓库名: $RepoName" -ForegroundColor White
    Write-Host "    设为 Public 或 Private 均可" -ForegroundColor White
    Write-Host "  2. 创建后，在终端运行：" -ForegroundColor White
    Write-Host "     git remote add origin https://github.com/<你的用户名>/$RepoName.git" -ForegroundColor Green
    Write-Host "     git branch -M main" -ForegroundColor Green
    Write-Host "     git push -u origin main" -ForegroundColor Green
    Write-Host ""
    Write-Host "  3. 进仓库 → Actions → Daily AI Digest → Run workflow 手动触发一次" -ForegroundColor Cyan
    exit 0
}

# 4. 通过 gh CLI 创建仓库并推送
$repoExists = gh repo view "$RepoName" --json name 2>$null
if (-not $repoExists) {
    gh repo create "$RepoName" --public --source=. --remote=origin --push
    Write-Host "✅ 仓库已创建并推送" -ForegroundColor Green
} else {
    git remote add origin "https://github.com/$((gh api user).login)/$RepoName.git" 2>$null
    git branch -M main
    git push -u origin main
    Write-Host "✅ 已推送到现有仓库" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 部署完成！" -ForegroundColor Cyan
Write-Host "   前往 https://github.com/<你的用户名>/$RepoName 查看" -ForegroundColor White
Write-Host "   进入 Actions → Daily AI Digest → Run workflow 手动触发测试" -ForegroundColor White
