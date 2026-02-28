#!/usr/bin/env bash
# Sound Hooks - Claude Code 通知脚本
# 用法: ./notify.sh "消息" [stage]

set -euo pipefail

# 确定插件根目录，如果环境变量未设置则使用当前目录
# 从 scripts/ 目录向上一级到达插件根目录
: "${CLAUDE_PLUGIN_ROOT:=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

MESSAGE="${1:-Claude Code 通知}"
STAGE="${2:-default}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 默认配置
DEFAULT_ENABLED=true
DEFAULT_NOTIFY_ENABLED=true
DEFAULT_SOUND="Glass"

# macOS 可用声音列表
MAC_SOUNDS=(
    "Basso" "Blow" "Bottle" "Frog" "Funk" "Glass"
    "Hero" "Morse" "Ping" "Pop" "Purr" "Sosumi"
    "Submarine" "Tink"
)

# 加载配置
load_config() {
    local config_file="${CLAUDE_PLUGIN_ROOT}/config.json"

    if [ ! -f "$config_file" ]; then
        return 1
    fi

    # 使用 jq 解析 JSON (如果可用)
    if command -v jq &> /dev/null; then
        enabled=$(jq -r '.enabled // true' "$config_file" 2>/dev/null || echo "true")
        notify_enabled=$(jq -r '.notifications.enabled // true' "$config_file" 2>/dev/null || echo "true")
        sound=$(jq -r '.notifications.sounds."$STAGE" // .notifications.sound // "Glass"' "$config_file" 2>/dev/null || echo "Glass")
        stage_enabled=$(jq -r ".stages.$STAGE // true" "$config_file" 2>/dev/null || echo "true")
        log_enabled=$(jq -r '.notifications.log // false' "$config_file" 2>/dev/null || echo "false")
        log_file=$(jq -r '.notifications.log_file // ""' "$config_file" 2>/dev/null || echo "")
    else
        enabled="true"
        notify_enabled="true"
        sound="Glass"
        stage_enabled="true"
        log_enabled="false"
        log_file=""
    fi

    # 展开 log_file 中的变量
    if [ -n "$log_file" ]; then
        log_file=$(eval echo "$log_file")
    fi
}

# 验证声音是否有效
validate_sound() {
    local sound="$1"
    if [[ "$(uname -s)" == "Darwin" ]]; then
        for s in "${MAC_SOUNDS[@]}"; do
            if [[ "$s" == "$sound" ]]; then
                echo "$sound"
                return 0
            fi
        done
        # 检查是否为自定义音效文件
        local custom_sound="${CLAUDE_PLUGIN_ROOT}/src/sounds/${sound}.mp3"
        if [ -f "$custom_sound" ]; then
            echo "$sound"
            return 0
        fi
        echo "Glass"
    else
        echo "$sound"
    fi
}

# 根据事件选择 emoji
get_emoji() {
    case "$1" in
        SessionStart)        echo "🔄" ;;
        UserPromptSubmit)    echo "✏️" ;;
        PreToolUse)         echo "🔧" ;;
        PermissionRequest)    echo "🔐" ;;
        PostToolUse)        echo "✓" ;;
        PostToolUseFailure)  echo "✗" ;;
        Notification)        echo "📢" ;;
        SubagentStart)       echo "🤖" ;;
        SubagentStop)        echo "🛑" ;;
        Stop)               echo "🏁" ;;
        TeammateIdle)        echo "💤" ;;
        TaskCompleted)       echo "🎉" ;;
        PreCompact)          echo "📦" ;;
        SessionEnd)          echo "👋" ;;
        task_start)         echo "🚀" ;;
        task_complete)       echo "✅" ;;
        task_in_progress)    echo "⏳" ;;
        task_error)          echo "❌" ;;
        command_start)       echo "⚡" ;;
        command_complete)    echo "⏱️" ;;
        *)                  echo "🔔" ;;
    esac
}

# 发送通知
send_notification() {
    local msg="$1"
    local snd="$2"
    local is_custom_sound=""

    case "$(uname -s)" in
        Darwin*)
            # 先检查是否为自定义音效
            local custom_sound="${CLAUDE_PLUGIN_ROOT}/src/sounds/${snd}.mp3"
            if [ -f "$custom_sound" ]; then
                # 使用 nohup 确保后台进程能继续运行
                (nohup afplay "$custom_sound" > /dev/null 2>&1 &)
                is_custom_sound="true"
            else
                # 使用系统声音
                local sound_file="/System/Library/Sounds/${snd}.aiff"
                if [ -f "$sound_file" ]; then
                    (nohup afplay "$sound_file" > /dev/null 2>&1 &)
                fi
            fi
            # 只在使用系统声音时设置 sound name，避免自定义声音播放两次
            if [ "$is_custom_sound" != "true" ]; then
                osascript -e "display notification \"$msg\" with title \"$(get_emoji $STAGE) Claude Code\" sound name \"$snd\"" 2>/dev/null || true
            else
                osascript -e "display notification \"$msg\" with title \"$(get_emoji $STAGE) Claude Code\"" 2>/dev/null || true
            fi
            ;;
        Linux*)
            if command -v notify-send &> /dev/null; then
                notify-send "Claude Code" "$msg" 2>/dev/null || true
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            if command -v powershell &> /dev/null; then
                powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('$msg', 'Claude Code')" 2>/dev/null || true
            fi
            ;;
    esac
}

# 主逻辑
main() {
    # 加载配置
    load_config || {
        enabled="$DEFAULT_ENABLED"
        notify_enabled="$DEFAULT_NOTIFY_ENABLED"
        sound="$DEFAULT_SOUND"
        stage_enabled="true"
        log_enabled="false"
        log_file=""
    }

    # 检查是否启用
    if [[ "$enabled" != "true" ]] || [[ "$notify_enabled" != "true" ]] || [[ "$stage_enabled" != "true" ]]; then
        exit 0
    fi

    # 验证声音
    sound=$(validate_sound "$sound")

    # 发送通知
    send_notification "$MESSAGE" "$sound"

    # 输出到 stdout
    echo "[$TIMESTAMP] $(get_emoji $STAGE) [$STAGE] $MESSAGE"

    # 写入日志文件
    if [[ "$log_enabled" == "true" ]] && [[ -n "$log_file" ]]; then
        mkdir -p "$(dirname "$log_file")" 2>/dev/null || true
        echo "[$TIMESTAMP] $(get_emoji $STAGE) [$STAGE] $MESSAGE" >> "$log_file" || true
    fi
}

main "$@"
