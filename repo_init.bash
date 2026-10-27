#!/usr/bin/env bash
# ==============================================================================
# Text2SQL1021 仓库初始化与双远端/双分支配置脚本
# 
# 配置说明:
# 1. 双远端 (Dual Remotes):
#    - origin : GitHub 个人开发仓库 (https://github.com/kemuriame4/Text2SQL1021.git)
#               用于日常开发推送 (push / fetch)
#    - aliyun : 阿里云 Codeup 团队上游仓库 (https://codeup.aliyun.com/66f42a489d3c82efe37ae9b9/Text2SQL1021.git)
#               仅用于同步团队更新 (fetch only, push 设置为 no_push 防误推)
#
# 2. 双分支 (Dual Branches):
#    - main   : 本地开发主分支，跟踪 origin/main
#    - master : 本地上游同步分支，跟踪 aliyun/master
# ==============================================================================

set -euo pipefail

# 颜色输出定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 检查是否在 Git 仓库根目录
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    warn "当前目录未初始化 Git 仓库，正在执行 git init..."
    git init
    git branch -M main
fi

info "开始配置 Git 双远端与双分支..."

GITHUB_REMOTE_URL="https://github.com/kemuriame4/Text2SQL1021.git"
ALIYUN_REMOTE_URL="https://codeup.aliyun.com/66f42a489d3c82efe37ae9b9/Text2SQL1021.git"

# 2. 配置 origin (GitHub) 远端
info "配置 origin 远端 -> ${GITHUB_REMOTE_URL}"
if git remote | grep -q "^origin$"; then
    git remote set-url origin "${GITHUB_REMOTE_URL}"
    git remote set-url --push origin "${GITHUB_REMOTE_URL}"
else
    git remote add origin "${GITHUB_REMOTE_URL}"
fi
success "origin 远端配置完成 (支持 fetch / push)"

# 3. 配置 aliyun (阿里云 Codeup) 远端
info "配置 aliyun 远端 -> ${ALIYUN_REMOTE_URL}"
if git remote | grep -q "^aliyun$"; then
    git remote set-url aliyun "${ALIYUN_REMOTE_URL}"
else
    git remote add aliyun "${ALIYUN_REMOTE_URL}"
fi

# 关键安全配置：防止误推到团队 aliyun 仓库
info "设置 aliyun 远端为只读 (pushurl = no_push)"
git remote set-url --push aliyun no_push
success "aliyun 远端配置完成 (只拉取，防误推)"

# 4. 获取远端分支信息
info "正在拉取远端分支元数据 (git fetch)..."
git fetch origin || warn "无法连接到 origin (GitHub)，请检查网络或代理"
git fetch aliyun || warn "无法连接到 aliyun (Codeup)，请检查网络或权限"

# 5. 配置双分支跟踪 (main <-> origin/main, master <-> aliyun/master)
# 5.1 确保本地在 main 分支并跟踪 origin/main
if git show-ref --verify --quiet refs/heads/main; then
    info "本地已存在 main 分支，关联跟踪 origin/main..."
    git checkout -q main
else
    info "创建 main 分支并跟踪 origin/main..."
    if git show-ref --verify --quiet refs/remotes/origin/main; then
        git checkout -b main --track origin/main
    else
        git checkout -b main
    fi
fi

if git show-ref --verify --quiet refs/remotes/origin/main; then
    git branch -u origin/main main 2>/dev/null || true
fi
success "main 分支已配置，跟踪 origin/main"

# 5.2 配置 master 分支跟踪 aliyun/master
if git show-ref --verify --quiet refs/remotes/aliyun/master; then
    if git show-ref --verify --quiet refs/heads/master; then
        info "本地已存在 master 分支，关联跟踪 aliyun/master..."
        git branch -u aliyun/master master 2>/dev/null || true
    else
        info "创建本地 master 分支并跟踪 aliyun/master..."
        git branch --track master aliyun/master
    fi
    success "master 分支已配置，跟踪 aliyun/master"
else
    warn "未发现 aliyun/master 远程分支，跳过本地 master 自动跟踪创建"
fi

# 6. 配置便捷 Git 别名 (本地仓库有效)
info "配置日常同步快捷别名 (git alias)..."
# 同步阿里云 master 更新到当前分支
git config alias.sync-upstream '!git fetch aliyun && git merge aliyun/master'
# 快速更新本地 master 分支为最新 aliyun/master (无需切换分支)
git config alias.sync-master '!git fetch aliyun master:master'
# 快速推送到 GitHub main
git config alias.push-main 'push origin main'
success "Git 快捷别名配置完成"

# 7. 打印配置结果与常用工作流
echo ""
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}           Text2SQL1021 Git 双源/双分支环境初始化完成！                         ${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo ""
info "【当前 Remote 配置】:"
git remote -v
echo ""
info "【当前本地分支与跟踪关系】:"
git branch -vv
echo ""
echo -e "${BLUE}【推荐日常协同工作流】:${NC}"
echo "  1. 拉取团队最新代码并合并到当前开发分支 (main):"
echo "     git sync-upstream   # 等价于: git fetch aliyun && git merge aliyun/master"
echo "  2. 提交本地改动并推送到个人 GitHub 仓库:"
echo "     git add ."
echo "     git commit -m \"your commit message\""
echo "     git push origin main"
echo "  3. 静默同步本地 master 分支（无需切换分支）:"
echo "     git sync-master     # 等价于: git fetch aliyun master:master"
echo "=============================================================================="
