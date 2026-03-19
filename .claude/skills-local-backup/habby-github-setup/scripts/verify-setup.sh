#!/bin/bash

# Habby GitHub 配置验证脚本
# 用于快速诊断 gh 和 git 配置状态

set -e

HOSTNAME="habby.ghe.com"

echo "========================================"
echo "Habby GitHub 配置诊断工具"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    local cmd=$1
    local name=$2

    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name 已安装"
        return 0
    else
        echo -e "${RED}✗${NC} $name 未安装"
        return 1
    fi
}

# 分隔线
separator() {
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 1. 系统信息
echo "【1. 系统信息】"
echo "操作系统: $(sw_vers -productName) $(sw_vers -productVersion)"
echo "芯片架构: $(uname -m)"
echo "Shell: $SHELL"

separator

# 2. 工具检查
echo "【2. 工具检查】"
check_command "gh" "GitHub CLI (gh)"
GH_INSTALLED=$?

check_command "git" "Git"
GIT_INSTALLED=$?

check_command "brew" "Homebrew"
BREW_INSTALLED=$?

if [ $GH_INSTALLED -eq 0 ]; then
    echo "  gh 版本: $(gh --version | head -n 1)"
    echo "  gh 路径: $(which gh)"
fi

if [ $GIT_INSTALLED -eq 0 ]; then
    echo "  git 版本: $(git --version)"
    echo "  git 路径: $(which git)"
fi

if [ $BREW_INSTALLED -eq 0 ]; then
    echo "  brew 版本: $(brew --version | head -n 1)"
fi

separator

# 3. gh 认证状态
echo "【3. gh 认证状态】"
if [ $GH_INSTALLED -eq 0 ]; then
    if gh auth status --hostname "$HOSTNAME" &> /dev/null; then
        echo -e "${GREEN}✓${NC} 已登录到 $HOSTNAME"
        echo ""
        gh auth status --hostname "$HOSTNAME"
        GH_LOGGED_IN=0
    else
        echo -e "${RED}✗${NC} 未登录到 $HOSTNAME"
        echo ""
        echo "请运行以下命令登录："
        echo "  gh auth login --hostname $HOSTNAME"
        GH_LOGGED_IN=1
    fi
else
    echo -e "${YELLOW}⚠${NC} gh CLI 未安装，无法检查认证状态"
    GH_LOGGED_IN=1
fi

separator

# 3.5. Token Scopes 检查
echo "【3.5. Token 权限检查】"
if [ $GH_INSTALLED -eq 0 ] && [ $GH_LOGGED_IN -eq 0 ]; then
    echo "检查必需的 Token scopes..."
    echo ""

    # 获取 auth status 输出（强制使用 stderr 重定向）
    # 使用临时文件避免子shell变量丢失问题
    TEMP_AUTH_FILE=$(mktemp)
    gh auth status --hostname "$HOSTNAME" > "$TEMP_AUTH_FILE" 2>&1 || true
    AUTH_OUTPUT=$(cat "$TEMP_AUTH_FILE")
    rm -f "$TEMP_AUTH_FILE"

    # 必需的 scopes
    REQUIRED_SCOPES=("repo" "read:org" "workflow")
    MISSING_SCOPES=()

    for scope in "${REQUIRED_SCOPES[@]}"; do
        # 使用更灵活的匹配方式，支持带引号和不带引号的格式
        if echo "$AUTH_OUTPUT" | grep -E "(Token scopes|scopes).*['\"]?${scope}['\"]?" > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $scope"
        else
            echo -e "${RED}✗${NC} $scope (缺失)"
            MISSING_SCOPES+=("$scope")
        fi
    done

    echo ""
    if [ ${#MISSING_SCOPES[@]} -eq 0 ]; then
        echo -e "${GREEN}✓${NC} 所有必需权限已配置"
    else
        echo -e "${RED}✗${NC} 缺少必需权限: ${MISSING_SCOPES[*]}"
        echo ""
        echo "解决方案："
        echo "  gh auth refresh --hostname $HOSTNAME --scopes repo,read:org,workflow"
        echo ""
        echo "或重新登录："
        echo "  gh auth logout --hostname $HOSTNAME"
        echo "  gh auth login --hostname $HOSTNAME"
    fi
else
    echo -e "${YELLOW}⚠${NC} 跳过（未登录或 gh CLI 未安装）"
fi

separator

# 4. git 配置检查
echo "【4. git 配置检查】"
if [ $GIT_INSTALLED -eq 0 ]; then
    echo "Credential Helper:"
    git config --global credential.helper || echo "  未配置"

    echo ""
    echo "代理设置:"
    git config --global http.proxy || echo "  http.proxy: 未配置"
    git config --global https.proxy || echo "  https.proxy: 未配置"

    echo ""
    echo "SSL 验证:"
    SSL_VERIFY=$(git config --global http.sslVerify || echo "true")
    echo "  http.sslVerify: $SSL_VERIFY"
else
    echo -e "${YELLOW}⚠${NC} git 未安装，无法检查配置"
fi

separator

# 5. 网络连通性检查
echo "【5. 网络连通性检查】"

echo "DNS 解析:"
if nslookup "$HOSTNAME" &> /dev/null; then
    echo -e "${GREEN}✓${NC} $HOSTNAME DNS 解析成功"
else
    echo -e "${RED}✗${NC} $HOSTNAME DNS 解析失败"
fi

echo ""
echo "HTTPS 连接:"
if curl -I "https://$HOSTNAME" --max-time 5 &> /dev/null; then
    echo -e "${GREEN}✓${NC} 能够连接 https://$HOSTNAME"
else
    echo -e "${RED}✗${NC} 无法连接 https://$HOSTNAME"
    echo "  提示: 请检查 VPN 或网络连接"
fi

separator

# 6. 环境变量检查
echo "【6. 环境变量检查】"
echo "PATH (前 3 个目录):"
echo "$PATH" | tr ':' '\n' | head -n 3 | sed 's/^/  /'

echo ""
echo "代理环境变量:"
if [ -n "$HTTP_PROXY" ]; then
    echo "  HTTP_PROXY: $HTTP_PROXY"
else
    echo "  HTTP_PROXY: 未设置"
fi

if [ -n "$HTTPS_PROXY" ]; then
    echo "  HTTPS_PROXY: $HTTPS_PROXY"
else
    echo "  HTTPS_PROXY: 未设置"
fi

if [ -n "$NO_PROXY" ]; then
    echo "  NO_PROXY: $NO_PROXY"
else
    echo "  NO_PROXY: 未设置"
fi

separator

# 7. API 测试
echo "【7. API 连通性测试】"
if [ $GH_INSTALLED -eq 0 ]; then
    if gh auth status --hostname "$HOSTNAME" &> /dev/null; then
        echo "测试 gh api user..."
        if gh api --hostname "$HOSTNAME" user &> /dev/null; then
            USER_LOGIN=$(gh api --hostname "$HOSTNAME" user | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
            echo -e "${GREEN}✓${NC} API 连接成功"
            echo "  登录用户: $USER_LOGIN"
            API_SUCCESS=0
        else
            echo -e "${RED}✗${NC} API 连接失败"
            echo "  提示: Token 可能已过期，尝试运行: gh auth refresh --hostname $HOSTNAME"
            API_SUCCESS=1
        fi
    else
        echo -e "${YELLOW}⚠${NC} 跳过（未登录）"
        API_SUCCESS=1
    fi
else
    echo -e "${YELLOW}⚠${NC} 跳过（gh CLI 未安装）"
    API_SUCCESS=1
fi

separator

# 7.5. habby 组织成员检查（关键！）
echo "【7.5. habby 组织成员检查】"
ORG_NAME="habby"
IS_ORG_MEMBER=1

if [ $GH_INSTALLED -eq 0 ] && [ $API_SUCCESS -eq 0 ]; then
    echo "检查你是否是 $ORG_NAME 组织成员..."
    echo ""

    # 获取当前用户名
    CURRENT_USER=$(gh api --hostname "$HOSTNAME" user --jq '.login' 2>/dev/null)

    if [ -n "$CURRENT_USER" ]; then
        echo "当前用户: $CURRENT_USER"
        echo ""

        # 检查组织成员资格
        if gh api --hostname "$HOSTNAME" "orgs/$ORG_NAME/memberships/$CURRENT_USER" &> /dev/null; then
            MEMBERSHIP_STATE=$(gh api --hostname "$HOSTNAME" "orgs/$ORG_NAME/memberships/$CURRENT_USER" --jq '.state' 2>/dev/null)

            if [ "$MEMBERSHIP_STATE" = "active" ]; then
                echo -e "${GREEN}✓${NC} 你是 $ORG_NAME 组织的成员（状态: active）"
                IS_ORG_MEMBER=0
            else
                echo -e "${YELLOW}⚠${NC} 你的组织成员状态为: $MEMBERSHIP_STATE"
                echo "  可能需要接受组织邀请"
            fi
        else
            echo -e "${RED}✗${NC} 你不是 $ORG_NAME 组织的成员"
            echo ""
            echo -e "${RED}🚨 重要提示：${NC}"
            echo ""
            echo "  即使 gh 登录成功，你也无法访问 $ORG_NAME 组织下的仓库。"
            echo ""
            echo "  请联系运维同事，将你的账号添加到 $ORG_NAME 组织中。"
            echo ""
            echo "  需要提供的信息："
            echo "    - 企业版 GitHub 用户名: $CURRENT_USER"
            echo "    - 需要加入的组织: $ORG_NAME"
            echo ""
        fi
    else
        echo -e "${RED}✗${NC} 无法获取当前用户名"
    fi
else
    echo -e "${YELLOW}⚠${NC} 跳过（gh CLI 未安装或 API 连接失败）"
fi

separator

# 8. gh 配置文件检查
echo "【8. gh 配置文件】"
GH_CONFIG="$HOME/.config/gh/hosts.yml"
if [ -f "$GH_CONFIG" ]; then
    echo "配置文件路径: $GH_CONFIG"
    echo ""
    if grep -q "$HOSTNAME" "$GH_CONFIG"; then
        echo -e "${GREEN}✓${NC} 找到 $HOSTNAME 配置"
        echo ""
        echo "配置内容:"
        grep -A 5 "$HOSTNAME" "$GH_CONFIG" | sed 's/^/  /'
    else
        echo -e "${YELLOW}⚠${NC} 未找到 $HOSTNAME 配置"
    fi
else
    echo -e "${YELLOW}⚠${NC} 配置文件不存在: $GH_CONFIG"
fi

separator

# 9. 总结和建议
echo "【9. 诊断总结】"
echo ""

ISSUES=0

if [ $GH_INSTALLED -ne 0 ]; then
    echo -e "${RED}✗${NC} gh CLI 未安装"
    echo "   解决方案: brew install gh"
    ISSUES=$((ISSUES + 1))
fi

if [ $GH_INSTALLED -eq 0 ] && ! gh auth status --hostname "$HOSTNAME" &> /dev/null; then
    echo -e "${RED}✗${NC} 未登录到 $HOSTNAME"
    echo "   解决方案: gh auth login --hostname $HOSTNAME"
    ISSUES=$((ISSUES + 1))
fi

if [ $GH_INSTALLED -eq 0 ] && [ $GH_LOGGED_IN -eq 0 ] && [ ${#MISSING_SCOPES[@]} -gt 0 ]; then
    echo -e "${RED}✗${NC} Token 缺少必需权限: ${MISSING_SCOPES[*]}"
    echo "   解决方案: gh auth refresh --hostname $HOSTNAME --scopes repo,read:org,workflow"
    ISSUES=$((ISSUES + 1))
fi

if [ $GH_INSTALLED -eq 0 ] && [ $API_SUCCESS -eq 0 ] && [ $IS_ORG_MEMBER -ne 0 ]; then
    CURRENT_USER_CHECK=$(gh api --hostname "$HOSTNAME" user --jq '.login' 2>/dev/null)
    echo -e "${RED}✗${NC} 不是 $ORG_NAME 组织成员"
    echo "   解决方案: 联系运维同事，将账号 $CURRENT_USER_CHECK 添加到 $ORG_NAME 组织"
    ISSUES=$((ISSUES + 1))
fi

if ! curl -I "https://$HOSTNAME" --max-time 5 &> /dev/null; then
    echo -e "${RED}✗${NC} 无法连接 $HOSTNAME"
    echo "   解决方案: 检查 VPN 或网络连接"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✓ 配置正常！${NC}"
    echo ""
    echo "你现在可以："
    echo "  - 使用 gh 命令操作企业版仓库"
    echo "  - 使用 git clone/pull/push 访问 $HOSTNAME 仓库"
else
    echo ""
    echo "发现 $ISSUES 个问题，请按上述建议修复。"
    echo ""
    echo "更多帮助，请查看:"
    echo "  .claude/skills/habby-github-setup/TROUBLESHOOTING.md"
fi

separator

echo "诊断完成！"
echo ""
