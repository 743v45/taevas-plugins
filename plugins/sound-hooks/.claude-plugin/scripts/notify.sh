#!/usr/bin/env bash
# Sound Hooks - Claude Code 通知脚本
# 用法: ./notify.sh "消息" [stage]

set -euo pipefail

MESSAGE="${1:-Claude Code 通知}"
STAGE="${2:-default}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# 默认配置
DEFAULT_ENABLED=true
DEFAULT_NOTIFY_ENABLED=true
DEFAULT_SOUND="Glass"
DEFAULT_LOG=true
DEFAULT_LOG_FILE="${CLAUDE_PLUGIN_ROOT}/notifications.log"

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
        log=$(jq -r '.notifications.log // true' "$config_file" 2>/dev/null || echo "true")
        log_file=$(jq -r '.notifications.log_file // "null"' "$config_file" 2>/dev/null)
        [ "$log_file" = "null" ] && log_file="${CLAUDE_PLUGIN_ROOT}/notifications.log"
        stage_enabled=$(jq -r ".stages.$STAGE // true" "$config_file" 2>/dev/null || echo "true")
    else
        enabled="true"
        notify_enabled="true"
        sound="Glass"
        log="true"
        log_file="${CLAUDE_PLUGIN_ROOT}/notifications.log"
        stage_enabled="true"
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

    case "$(uname -s)" in
        Darwin*)
            # 先确保声音文件存在
            local sound_file="/System/Library/Sounds/${snd}.aiff"
            if [ -f "$sound_file" ]; then
                # 使用 nohup 确保后台进程能继续运行
                (nohup afplay "$sound_file" > /dev/null 2>&1 &)
            fi
            osascript -e "display notification \"$msg\" with title \"$(get_emoji $STAGE) Claude Code\" sound name \"$snd\"" 2>/dev/null || true
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

# 写入日志
write_log() {
    local log_file="$1"
    local message="$2"
    local timestamp="$3"
    local stage="$4"

    local log_dir="$(dirname "$log_file")"
    [ ! -d "$log_dir" ] && mkdir -p "$log_dir"
    echo "[$timestamp] [$stage] $message" >> "$log_file"
}

# 主逻辑
main() {
    # 加载配置
    load_config || {
        enabled="$DEFAULT_ENABLED"
        notify_enabled="$DEFAULT_NOTIFY_ENABLED"
        sound="$DEFAULT_SOUND"
        log="$DEFAULT_LOG"
        log_file="$DEFAULT_LOG_FILE"
        stage_enabled="true"
    }

    # 检查是否启用
    if [[ "$enabled" != "true" ]] || [[ "$notify_enabled" != "true" ]] || [[ "$stage_enabled" != "true" ]]; then
        exit 0
    fi

    # 验证声音
    sound=$(validate_sound "$sound")

    # 写入日志
    if [[ "$log" == "true" ]]; then
        write_log "$log_file" "$MESSAGE" "$TIMESTAMP" "$STAGE"
    fi

    # 发送通知
    send_notification "$MESSAGE" "$sound"

    # 输出到 stdout
    echo "[$TIMESTAMP] $(get_emoji $STAGE) [$STAGE] $MESSAGE"
}

main "$@"
