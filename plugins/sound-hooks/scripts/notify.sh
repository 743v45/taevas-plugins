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
DEFAULT_SHOW_ENABLED=true
DEFAULT_SOUND_ENABLED=true
DEFAULT_SOUND="Glass"
DEFAULT_LOG_FILE="${CLAUDE_PLUGIN_ROOT}/notifications.log"

# macOS 可用声音列表
MAC_SOUNDS=(
    "Basso" "Blow" "Bottle" "Frog" "Funk" "Glass"
    "Hero" "Morse" "Ping" "Pop" "Purr" "Sosumi"
    "Submarine" "Tink"
)

# 写入日志
write_log() {
    local msg="$1"
    if [[ "$log_enabled" == "true" ]] && [[ -n "$log_file" ]]; then
        mkdir -p "$(dirname "$log_file")" 2>/dev/null || true
        echo "[$TIMESTAMP] $msg" >> "$log_file" 2>/dev/null || true
    fi
}

# 加载配置
load_config() {
    local config_file="${CLAUDE_PLUGIN_ROOT}/config.json"
    local load_error=""

    if [ ! -f "$config_file" ]; then
        load_error="Config file not found: $config_file"
    fi

    # 使用 jq 解析 JSON (如果可用)
    if [ -z "$load_error" ] && command -v jq &> /dev/null; then
        enabled=$(jq -r '.enabled // true' "$config_file" 2>/dev/null || echo "true")
        notify_enabled=$(jq -r '.notifications.enabled // true' "$config_file" 2>/dev/null || echo "true")
        show_enabled=$(jq -r --arg stage "$STAGE" '.notifications.show[$stage] // true' "$config_file" 2>/dev/null || echo "true")
        sound=$(jq -r --arg stage "$STAGE" '.notifications.sounds[$stage] // .notifications.sound // "Glass"' "$config_file" 2>/dev/null || echo "Glass")
        sound_enabled=$(jq -r --arg stage "$STAGE" '.sounds[$stage] // true' "$config_file" 2>/dev/null || echo "true")
        log_enabled=$(jq -r '.notifications.log // false' "$config_file" 2>/dev/null || echo "false")
        log_file=$(jq -r '.notifications.log_file // ""' "$config_file" 2>/dev/null || echo "")
    else
        enabled="true"
        notify_enabled="true"
        show_enabled="true"
        sound="Glass"
        sound_enabled="true"
        log_enabled="false"
        log_file=""
    fi

    # 如果没有成功加载配置，使用默认日志文件
    if [ -z "$log_file" ]; then
        log_file="$DEFAULT_LOG_FILE"
    fi

    # 展开 log_file 中的变量
    if [ -n "$log_file" ]; then
        log_file=$(eval echo "$log_file")
    fi

    # 记录配置加载错误
    if [ -n "$load_error" ]; then
        write_log "[ERROR] Config load failed: $load_error"
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
    local show_notification="${3:-true}"
    local with_sound="${4:-true}"
    local is_custom_sound=""

    case "$(uname -s)" in
        Darwin*)
            # 显示通知
            if [ "$show_notification" == "true" ]; then
                osascript -e "display notification \"$msg\" with title \"$(get_emoji $STAGE) Claude Code\"" 2>/dev/null || true
            fi
            # 播放声音
            if [ "$with_sound" == "true" ]; then
                local custom_sound="${CLAUDE_PLUGIN_ROOT}/src/sounds/${snd}.mp3"
                if [ -f "$custom_sound" ]; then
                    (nohup afplay "$custom_sound" > /dev/null 2>&1 &)
                else
                    local sound_file="/System/Library/Sounds/${snd}.aiff"
                    if [ -f "$sound_file" ]; then
                        (nohup afplay "$sound_file" > /dev/null 2>&1 &)
                    fi
                fi
            fi
            ;;
        Linux*)
            if [ "$show_notification" == "true" ] && command -v notify-send &> /dev/null; then
                notify-send "Claude Code" "$msg" 2>/dev/null || true
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            if [ "$show_notification" == "true" ] && command -v powershell &> /dev/null; then
                powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('$msg', 'Claude Code')" 2>/dev/null || true
            fi
            ;;
    esac
}

# 主逻辑
main() {
    # 加载配置（失败时会使用默认值并记录日志）
    if ! load_config; then
        enabled="$DEFAULT_ENABLED"
        notify_enabled="$DEFAULT_NOTIFY_ENABLED"
        show_enabled="$DEFAULT_SHOW_ENABLED"
        sound="$DEFAULT_SOUND"
        sound_enabled="$DEFAULT_SOUND_ENABLED"
        log_enabled="false"
        log_file="$DEFAULT_LOG_FILE"
    fi

    # 检查是否启用
    if [[ "$enabled" != "true" ]] || [[ "$notify_enabled" != "true" ]]; then
        exit 0
    fi

    # 如果不显示通知也不播放声音，则退出
    if [[ "$show_enabled" != "true" ]] && [[ "$sound_enabled" != "true" ]]; then
        exit 0
    fi

    # 验证声音
    sound=$(validate_sound "$sound")

    # 发送通知（分别控制通知显示和声音播放）
    send_notification "$MESSAGE" "$sound" "$show_enabled" "$sound_enabled"

    # 输出到 stdout
    local log_msg="[$TIMESTAMP] $(get_emoji $STAGE) [$STAGE] $MESSAGE"
    echo "$log_msg"

    # 写入日志文件
    if [[ "$log_enabled" == "true" ]] && [[ -n "$log_file" ]]; then
        write_log "$(get_emoji $STAGE) [$STAGE] $MESSAGE"
    fi
}

main "$@"
