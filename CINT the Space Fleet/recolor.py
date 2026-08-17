# -*- coding: utf-8 -*-
"""
CINT the Space Fleet / 2.md —— 颜色与加粗统一重排工具

用法:
    python3 recolor.py                # 就地重写同目录下的 2.md
    python3 recolor.py 输入.md 输出.md

配色与加粗的唯一来源是 annotate_cint2.py 里的 REG 表（避免两处重复配置）。
本脚本直接 import annotate_cint2 读取 REG，自动生成 角色ID -> (color, bold)
映射；对 2.md 中每处 <span ... data-char="X" ...>内容</span> 重新生成 style，
从而一键改色 / 改加粗。

要改某个角色的颜色或加粗，只改 annotate_cint2.py 里的 REG 即可，然后跑本脚本。
"""

import re
import sys
import os

# 让本脚本无论在哪运行都能 import 到同目录的 annotate_cint2.py
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import annotate_cint2 as _cfg

# ===== 唯一配色源：annotate_cint2.REG =====
# (color 十六进制 或 None, 是否加粗)；color 为 None 且 bold=False 时渲染为纯文本
COLOR = {cid: (d.get("color"), bool(d.get("bold"))) for cid, d in _cfg.REG.items()}
DEFAULT_COLOR = (None, False)

# 匹配 <span ... data-char="X" ...>内容</span>（本文件中的 span 不嵌套）
SPAN_RE = re.compile(
    r'<span\b[^>]*\bdata-char="([A-Za-z0-9_]+)"[^>]*>(.*?)</span>',
    re.DOTALL,
)

def rebuild(color, bold):
    style = ""
    if color:
        style += "color:#%s;" % color
    if bold:
        style += "font-weight:bold;"
    if style:
        return '<span style="%s" data-char="%%s">' % style
    return '<span data-char="%s">'

def recolor(text):
    def repl(m):
        cid = m.group(1)
        inner = m.group(2)
        color, bold = COLOR.get(cid, DEFAULT_COLOR)
        tmpl = rebuild(color, bold)
        return tmpl % cid + inner + "</span>"
    return SPAN_RE.sub(repl, text)

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "2.md")
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    with open(src, encoding="utf-8") as f:
        text = f.read()
    new = recolor(text)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(new)
    n = len(SPAN_RE.findall(text))
    print("处理完成：%s -> %s，共 %d 处 data-char 标注已按 annotate_cint2.py 的配色表重排。"
          % (src, dst, n))

if __name__ == "__main__":
    main()
