#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
peak-shift-studio 命令行入口。

用法::

    # 1) 先用引擎产出 JSON
    python ../peak-shift-engine/cli.py --tariff ../cn-tou-tariff/data/guangdong.json \\
        --preset ev_owner --format json > result.json

    # 2) 再由本工具渲染图表与报告
    python cli.py --input result.json --out output --html
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from studio import report  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="用电优化结果的图表与报告生成器")
    ap.add_argument("--input", required=True, help="peak-shift-engine 的 JSON 输出文件")
    ap.add_argument("--out", default="output", help="输出目录（默认 output）")
    ap.add_argument("--html", action="store_true", help="额外生成 HTML 报告")
    ap.add_argument("--title", default="用电时段优化报告", help="报告标题")
    args = ap.parse_args()

    try:
        payload = report.load_payload(args.input)
    except FileNotFoundError:
        print("错误：找不到输入文件 %s" % args.input, file=sys.stderr)
        return 2
    except Exception as e:
        print("错误：无法解析输入 JSON：%s" % e, file=sys.stderr)
        return 2

    paths = report.write_svgs(payload, args.out)
    for name, p in paths.items():
        print("  已生成  %s" % p)

    if args.html:
        svgs = {k: p.read_text(encoding="utf-8") for k, p in paths.items()}
        html = report.html_report(payload, svgs, title=args.title)
        out = Path(args.out) / "report.html"
        out.write_text(html, encoding="utf-8")
        print("  已生成  %s" % out)

    saving = payload.get("saving", 0)
    pct = payload.get("saving_pct", 0)
    print("\n%s：单次节省 ¥%.2f（%.1f%%），预计年省 ¥%.0f"
          % (payload.get("region") or "结果", saving, pct, payload.get("yearly_saving", 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
