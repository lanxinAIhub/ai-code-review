#!/bin/bash
# AI Code Review - 一键评审脚本

set -e

REVIEW_SCRIPT="$(dirname "$0")/src/reviewer.py"
OUTPUT="review-report.md"
PROVIDER="minimax"
PATH="."

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--provider)
            PROVIDER="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        *)
            PATH="$1"
            shift
            ;;
    esac
done

echo "🤖 AI Code Review"
echo "=================="
echo "路径: $PATH"
echo "Provider: $PROVIDER"
echo "输出: $OUTPUT"
echo ""

python3 "$REVIEW_SCRIPT" "$PATH" --provider "$PROVIDER" --output "$OUTPUT"

echo ""
echo "📋 报告已生成: $OUTPUT"
