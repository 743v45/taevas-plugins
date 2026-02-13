#!/usr/bin/env bash
# 显示 Git 仓库信息

if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "not a git repository"
    exit 0
fi

# 获取分支名
BRANCH=$(git branch --show-current 2>/dev/null || echo "HEAD")
# 获取 commit 数
COMMITS=$(git rev-list --count HEAD 2>/dev/null || echo "?")
# 获取远程
REMOTE=$(git remote get-url origin 2>/dev/null || echo "no remote")
# 获取状态
STATUS=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

if [ "$STATUS" -eq 0 ]; then
    STATUS_CLEAN="clean"
else
    STATUS_CLEAN="$STATUS changed"
fi

echo "[$BRANCH|$COMMITS|$STATUS_CLEAN]"
