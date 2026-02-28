#!/usr/bin/env bash
# Sound Hooks - Claude Code 通知脚本
# 用法: ./notify.sh [event_name]

set -euo pipefail

# 确定插件根目录
: "${CLAUDE_PLUGIN_ROOT:=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

EVENT="${1:-}"
STAGE="$EVENT"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 默认配置
DEFAULT_ENABLED=true
DEFAULT_EVENT_ENABLED=true
DEFAULT_NOTIFICATION=true
DEFAULT_SOUND_ENABLED=true
DEFAULT_SOUND="Glass"
DEFAULT_MESSAGE="Claude Code 通知"
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

    # 加载顶层配置
    if [ -z "$load_error" ] && command -v jq &> /dev/null; then
        enabled=$(jq -r '.enabled? // true' "$config_file" 2>/dev/null || echo "true")
        log_enabled=$(jq -r '.log? // false' "$config_file" 2>/dev/null || echo "false")
        log_file=$(jq -r '.log_file? // ""' "$config_file" 2>/dev/null || echo "")
    else
        enabled="$DEFAULT_ENABLED"
        log_enabled="false"
        log_file=""
    fi

    # 展开日志文件路径中的变量
    if [ -n "$log_file" ]; then
        log_file=$(eval echo "$log_file")
    fi

    # 如果没有成功加载配置，使用默认日志文件
    if [ -z "$log_file" ]; then
        log_file="$DEFAULT_LOG_FILE"
    fi

    # 如果没有指定事件，使用默认值
    if [ -z "$EVENT" ]; then
        event_enabled="$DEFAULT_EVENT_ENABLED"
        notification="$DEFAULT_NOTIFICATION"
        sound="$DEFAULT_SOUND"
        sound_enabled="$DEFAULT_SOUND_ENABLED"
        message="$DEFAULT_MESSAGE"
        return 0
    fi

    # 加载事件级配置
    if [ -z "$load_error" ] && command -v jq &> /dev/null; then
        event_enabled=$(jq -r --arg event "$EVENT" 'if .events[$event] | has("enabled") then .events[$event].enabled else true end' "$config_file" 2>/dev/null || echo "true")
        notification=$(jq -r --arg event "$EVENT" 'if .events[$event] | has("notification") then .events[$event].notification else true end' "$config_file" 2>/dev/null || echo "true")
        sound=$(jq -r --arg event "$EVENT" 'if .events[$event] | has("sound") then .events[$event].sound else "Glass" end' "$config_file" 2>/dev/null || echo "Glass")
        # 只有当事件配置存在且 sound 明确设为空字符串时才禁用声音
        sound_enabled=$(jq -r --arg event "$EVENT" 'if .events[$event] != null and (.events[$event].sound // "") == "" then false else true end' "$config_file" 2>/dev/null || echo "true")
        message=$(jq -r --arg event "$EVENT" 'if .events[$event] | has("message") then .events[$event].message else "Claude Code 通知" end' "$config_file" 2>/dev/null || echo "Claude Code 通知")
    else
        event_enabled="$DEFAULT_EVENT_ENABLED"
        notification="$DEFAULT_NOTIFICATION"
        sound="$DEFAULT_SOUND"
        sound_enabled="$DEFAULT_SOUND_ENABLED"
        message="$DEFAULT_MESSAGE"
    fi

    # 记录配置加载错误
    if [ -n "$load_error" ]; then
        write_log "[ERROR] Config load failed: $load_error"
        return 1
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
        PreToolUse)          echo "🔧" ;;
        PermissionRequest)   echo "🔐" ;;
        PostToolUse)         echo "✓" ;;
        PostToolUseFailure)  echo "✗" ;;
        Notification)        echo "📢" ;;
        SubagentStart)       echo "🤖" ;;
        SubagentStop)        echo "🛑" ;;
        Stop)                echo "🏁" ;;
        TeammateIdle)        echo "💤" ;;
        TaskCompleted)       echo "🎉" ;;
        PreCompact)          echo "📦" ;;
        SessionEnd)          echo "👋" ;;
        *)                   echo "🔔" ;;
    esac
}

# 发送通知
send_notification() {
    local msg="$1"
    local snd="$2"
    local show_notification="${3:-true}"
    local with_sound="${4:-true}"

    case "$(uname -s)" in
        Darwin*)
            # 显示通知（转义特殊字符避免 shell 注入）
            if [ "$show_notification" == "true" ]; then
                local title="$(get_emoji $STAGE) Claude Code"
                local escaped_msg=$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g')
                local escaped_title=$(printf '%s' "$title" | sed 's/\\/\\\\/g; s/"/\\"/g')
                osascript -e "display notification \"$escaped_msg\" with title \"$escaped_title\"" 2>/dev/null || true
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
    # 加载配置
    if ! load_config; then
        enabled="$DEFAULT_ENABLED"
        event_enabled="$DEFAULT_EVENT_ENABLED"
        notification="$DEFAULT_NOTIFICATION"
        sound="$DEFAULT_SOUND"
        sound_enabled="$DEFAULT_SOUND_ENABLED"
        message="$DEFAULT_MESSAGE"
        log_enabled="false"
        log_file="$DEFAULT_LOG_FILE"
    fi

    # 检查是否启用
    if [[ "$enabled" != "true" ]] || [[ "$event_enabled" != "true" ]]; then
        exit 0
    fi

    # 如果不显示通知也不播放声音，则退出
    if [[ "$notification" != "true" ]] && [[ "$sound_enabled" != "true" ]]; then
        exit 0
    fi

    # 验证声音
    sound=$(validate_sound "$sound")

    # 发送通知
    send_notification "$message" "$sound" "$notification" "$sound_enabled"

    # 输出到 stdout
    local log_msg="[$TIMESTAMP] $(get_emoji $STAGE) [$STAGE] $message"
    echo "$log_msg"

    # 写入日志文件
    if [[ "$log_enabled" == "true" ]] && [[ -n "$log_file" ]]; then
        write_log "$(get_emoji $STAGE) [$STAGE] $message"
    fi
}

main "$@"
