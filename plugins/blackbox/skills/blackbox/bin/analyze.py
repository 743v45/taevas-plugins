#!/usr/bin/env python3
"""
黑匣子埋点分析工具

用途：扫描代码中的黑匣子埋点，分析覆盖度，发现遗漏

使用：
    python bin/analyze.py <src目录>

示例：
    python bin/analyze.py src/
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, TypedDict
from glob import glob


class RecordPoint(TypedDict):
    file: str
    line: int
    type: str
    location: Optional[str]
    phase: Optional[str]
    hasTimestamp: bool
    hasContext: bool
    hasResources: bool


class AnalysisResult(TypedDict):
    totalPoints: int
    byType: Dict[str, int]
    byLocation: Dict[str, List[str]]
    byPhase: Dict[str, int]
    missingTypes: List[str]
    recommendations: List[str]


# 状态类型识别模式
STATE_PATTERNS = {
    'input': re.compile(r'inputs?|args?|parameters?|params?', re.IGNORECASE),
    'output': re.compile(r'output?|result?|return?|data?', re.IGNORECASE),
    'error': re.compile(r'error?|exception?|throw', re.IGNORECASE),
    'external': re.compile(r'response?|api?|fetch?|axios?|http', re.IGNORECASE),
    'context': re.compile(r'context?|user|session|request|url', re.IGNORECASE),
    'config': re.compile(r'config?|setting?|option?|flag?', re.IGNORECASE),
    'sequence': re.compile(r'sequence|previous|step', re.IGNORECASE),
    'time': re.compile(r'sequence|previous|step', re.IGNORECASE),
    'resources': re.compile(r'memory|cpu|connection|pool', re.IGNORECASE),
    'performance': re.compile(r'performance|timing|duration|elapsed', re.IGNORECASE),
}

# 代码模式到状态类型的映射
CODE_PATTERNS = [
    (re.compile(r'function\s*\(\s*\w+\s*,\s*\w+\s*\)'), 'input'),
    (re.compile(r'await\s+(fetch|axios|http\.)'), 'external'),
    (re.compile(r'catch\s*\(\s*\w+\s*\)\s*\{'), 'error'),
    (re.compile(r'page\.url\(\)'), 'context'),
    (re.compile(r'config\.\w+'), 'config'),
    (re.compile(r'Date\.now\(\)'), 'sequence'),
    (re.compile(r'db\.query|\.find|\.create|\.update|\.delete'), 'external'),
    (re.compile(r'process\.memoryUsage|cpuUsage'), 'resources'),
    (re.compile(r'performance\.now\(\)'), 'performance'),
    (re.compile(r'page\.screenshot|\.content\(\)'), 'snapshot'),
    (re.compile(r'for\s*\(.*?\)\s*\{|while\s*\(.*?\)\s*\{'), 'internal'),
]


def extract_value(line: str, key: str) -> Optional[str]:
    """从代码行中提取键值对"""
    pattern = re.compile(f'{key}\\s*:\\s*[\'"`]([^\'"`]+)[\'"`]')
    match = pattern.search(line)
    return match.group(1) if match else None


def analyze_file(file_path: str) -> List[RecordPoint]:
    """分析单个文件中的埋点"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    points: List[RecordPoint] = []

    for index, line in enumerate(lines):
        # 匹配黑匣子标记
        match = re.search(r'📦\s*\[BB\]\s*(\w+)?', line)
        if match:
            point: RecordPoint = {
                'file': file_path,
                'line': index + 1,
                'type': match.group(1) or 'STATE',
                'location': extract_value(line, 'location'),
                'phase': extract_value(line, 'phase'),
                'hasTimestamp': 'timestamp' in line,
                'hasContext': 'context' in line,
                'hasResources': 'resources' in line,
            }
            points.append(point)

    return points


def detect_missing_types(points: List[RecordPoint], content: str) -> List[str]:
    """检测缺失的状态类型"""
    missing: List[str] = []

    # 检查是否有外部响应但无时序记录
    has_external = any(
        p['type'] == 'STATE' and p['hasContext'] and 'response' in content
        for p in points
    )
    has_sequence = any(
        p['type'] == 'STATE' and 'sequence' in content
        for p in points
    )
    if has_external and not has_sequence:
        missing.append('时序状态（请求间隔）')

    # 检查是否有错误但无最后成功状态
    has_error = any(
        p['type'] == 'STATE' and 'error' in content
        for p in points
    )
    has_last_success = 'lastSuccessState' in content
    if has_error and not has_last_success:
        missing.append('失败前状态（最后成功状态）')

    # 检查是否有上下文但缺少关键信息
    has_context = any(p['hasContext'] for p in points)
    has_user_id = 'userId' in content
    has_request_id = 'requestId' in content
    if has_context and (not has_user_id or not has_request_id):
        missing.append('完整上下文（userId/requestId）')

    # 检查是否有资源监控
    has_resources = any(p['hasResources'] for p in points)
    has_long_operation = 'for' in content or 'while' in content
    if has_long_operation and not has_resources:
        missing.append('资源状态（内存监控）')

    return missing


def generate_recommendations(analysis: AnalysisResult) -> List[str]:
    """生成改进建议"""
    recommendations: List[str] = []

    # 基于类型的建议
    by_type = analysis['byType']
    if by_type.get('external', 0) > 0 and not by_type.get('sequence'):
        recommendations.append(
            '发现外部 API 调用，建议添加时序状态记录请求间隔'
        )

    if by_type.get('error', 0) > 0 and not by_type.get('lastSuccess'):
        recommendations.append(
            '发现错误处理，建议添加失败前的最后成功状态'
        )

    by_location = analysis['byLocation']
    if len(by_location) > 0:
        all_locations = [loc for locs in by_location.values() for loc in locs]
        has_trace_info = any(
            'userId' in loc or 'requestId' in loc for loc in all_locations
        )
        if not has_trace_info:
            recommendations.append(
                '建议在上下文中添加 userId 和 requestId 以增强追溯能力'
            )

    return recommendations


def analyze_directory(dir_path: str) -> AnalysisResult:
    """分析目录中的所有文件"""
    # 查找所有相关文件
    file_patterns = [
        os.path.join(dir_path, '**', '*.ts'),
        os.path.join(dir_path, '**', '*.js'),
        os.path.join(dir_path, '**', '*.tsx'),
        os.path.join(dir_path, '**', '*.jsx'),
        os.path.join(dir_path, '**', '*.py'),
    ]

    files = []
    for pattern in file_patterns:
        files.extend(glob(pattern, recursive=True))

    all_points: List[RecordPoint] = []

    for file in files:
        points = analyze_file(file)
        all_points.extend(points)

    # 按类型分组
    by_type: Dict[str, int] = {}
    for point in all_points:
        by_type[point['type']] = by_type.get(point['type'], 0) + 1

    # 按位置分组
    by_location: Dict[str, List[str]] = {}
    for point in all_points:
        if point['location']:
            if point['location'] not in by_location:
                by_location[point['location']] = []
            by_location[point['location']].append(point['file'])

    # 按阶段分组
    by_phase: Dict[str, int] = {}
    for point in all_points:
        if point['phase']:
            by_phase[point['phase']] = by_phase.get(point['phase'], 0) + 1

    # 检测缺失类型
    all_content = ''
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            all_content += f.read() + '\n'

    missing_types = detect_missing_types(all_points, all_content)

    # 生成建议
    recommendations = generate_recommendations({
        'totalPoints': len(all_points),
        'byType': by_type,
        'byLocation': by_location,
        'byPhase': by_phase,
        'missingTypes': [],
        'recommendations': [],
    })

    return {
        'totalPoints': len(all_points),
        'byType': by_type,
        'byLocation': by_location,
        'byPhase': by_phase,
        'missingTypes': missing_types,
        'recommendations': recommendations,
    }


def print_result(result: AnalysisResult) -> None:
    """打印分析结果"""
    print('\n✅ 已发现埋点:')
    print(f'   总计: {result["totalPoints"]} 个\n')

    print('📊 状态类型分布:')
    for state_type, count in result['byType'].items():
        print(f'   - {state_type}: {count}')

    if result['byPhase']:
        print('\n⏱️ 观测阶段分布:')
        for phase, count in result['byPhase'].items():
            print(f'   - {phase}: {count}')

    if result['missingTypes']:
        print('\n⚠️ 发现遗漏:')
        for missing in result['missingTypes']:
            print(f'   - {missing}')

    if result['recommendations']:
        print('\n💡 建议:')
        for index, rec in enumerate(result['recommendations'], 1):
            print(f'   {index}. {rec}')


def main():
    """主函数"""
    args = sys.argv[1:]
    dir_path = args[0] if args else 'src/'

    if not os.path.isdir(dir_path):
        print(f'错误: 目录不存在: {dir_path}', file=sys.stderr)
        sys.exit(1)

    print(f'扫描目录: {dir_path}')

    try:
        result = analyze_directory(dir_path)
        print_result(result)
    except Exception as error:
        print(f'分析失败: {error}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
