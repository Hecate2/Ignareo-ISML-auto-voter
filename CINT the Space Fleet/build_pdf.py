# -*- coding: utf-8 -*-
"""
build_pdf.py — 把带脚注的 Markdown 渲染成「脚注编号保留原样(42–72) + 可点击跳转」的 PDF。

流程:
  1) pandoc 把 .md 转成独立 HTML（忠实保留 <span> 配色、脚注锚点）。
  2) Python 后处理:
       - 把 pandoc 自动编号 1..N 还原成你 .md 里的原始标签（42–72）。
         映射方式 = 用「脚注定义正文」回匹配源文件里的 [^标签]: 定义，
         因此即使有重复引用（如 59 被引两次）也能正确归位。
       - 关闭脚注区 <ol> 的自动编号（pandoc 3.x 把 class 放在 <section> 上、
         <ol> 上没有 class，所以必须用正则定位），改为在正文里显示原始编号。
       - 把原始编号放进脚注文本行内（原来编号独占一行）。
       - 合并重复脚注（59 被引两次 -> 只保留一条定义，两个正文链接都跳过去；
         第二个正文锚点改叫 fnref59-2，避免 PDF 里出现重复锚点名）。
       - 注入可配置的全局字号 / 行距 / 页边距等。
  3) weasyprint 把 HTML 转成 PDF（内部锚点 -> 可点击跳转）。
     图片由 weasyprint 以无损 PNG 嵌入（源为 WebP 时像素不变）。
  4) 按画质档位用 Ghostscript 把嵌入图片降采样成 JPEG（默认 high=150 DPI，
     体积可省 ~85%，画质损失很小）。档位在 CONFIG 的 QUALITY 或命令行 --quality 里设。

只改下面 CONFIG 区块即可：最常改的是 BASE_FONT_SIZE_PT（正文文字大小，单位 pt）。
依赖: pandoc、weasyprint、ghostscript（本机已装）。运行:
    python3 build_pdf.py                          # 用 CONFIG 里的默认画质档位
    python3 build_pdf.py --font 12                # 临时覆盖字号
    python3 build_pdf.py --quality lossless       # 无损（图片不压缩）
    python3 build_pdf.py --quality low            # 更小体积（72 DPI）
    python3 build_pdf.py --quality 120            # 任意 DPI 数值
    python3 build_pdf.py --bold heavy             # 最强加粗：宋体 Heavy/Black 主字重
    python3 build_pdf.py --bold 900               # 宋体 Heavy（唯一能命中更重主字重的数值：
                                                  #   只有 100 的整数倍才被承认，700/800=Bold、900=Heavy）
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import zlib

# ============================ CONFIG（你主要改这里）============================
HERE = os.path.dirname(os.path.abspath(__file__))

SOURCE_MD = os.path.join(HERE, "2.md")          # 源 Markdown
OUTPUT_PDF = os.path.join(HERE, "2.pdf")        # 输出的 PDF（会覆盖同名文件）

# —— 文字大小（最常用）——
BASE_FONT_SIZE_PT = 16.0     # 正文基础字号（pt）。想大一点就改 12 / 13，小一点改 10。
FOOTNOTE_FONT_RATIO = 0.85   # 脚注区字号 = 正文 × 该比例
LINE_HEIGHT = 1.382            # 行距（段内行与行的距离）

# —— 段落间距 ——
PARAGRAPH_GAP_EM = 0.8       # 段落间距（em，相对字号）。0 = 段落紧贴（只剩行距）
FOOTNOTE_GAP_EM = 0.3        # 脚注区内的段落间距（脚注通常要更紧凑）

# —— 页面 ——
PAGE_SIZE = "A4"             # A4 / A5 / Letter ...
PAGE_MARGIN = "18mm"         # 页边距（上下左右统一）
MAX_CONTENT_WIDTH = "40em"   # 正文最大宽度（控制每行字数，留空则不限）

# —— 字体（CJK 优先；若缺字改成你系统有的中文字体）——
FONT_FAMILY = '"Songti SC", "STSong", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", serif'

# —— 加粗强度 ——
# ⚠️ 关键坑：WeasyPrint 只承认 font-weight 为 100 的整数倍（100/200/…/900）或
#   关键字（normal/bold/heavy…）。像 899、850、901 这类「非整数倍」数值会被
#   【静默忽略】，加粗元素于是退回浏览器默认 bold(700) = Songti-SC-Bold，
#   表现为「怎么调字重都没更粗」。这正是之前默认 899 不够粗的根因。
# 本机 Songti SC 真实只提供四档可见字重：Light(300)/Regular(400)/Bold(700)/Heavy(900)。
#   - 700 / 800 都映射到 Bold（800 也退 Bold，因为没有更重的中间字重）
#   - 只有 900 能命中 Songti-SC-Heavy（黑体，同一宋体家族，约 +25% 墨量，肉眼更粗）
# 结论：要「更粗」就把加粗设成 900（或 "heavy"）。这就是为什么默认就是 900。
BOLD_STRENGTH = 700   # normal(700) / heavy(900) / 仅限 100 的整数倍，否则被无视

BOLD_WEIGHT_PRESETS = {
    "normal": 700,   # 宋体 Bold（常规加粗）
    "heavy":  900,   # 宋体 Heavy/Black（明显更粗，同一宋体家族）
}

# —— 脚注视觉 ——
FOOTNOTE_RULE = True         # 脚注区上方是否画一条分隔线

# —— 图片画质档位（体积 vs 画质权衡）——
# 档位: lossless(无损) / high(150dpi, 推荐) / medium(96dpi) / low(72dpi)，
#       也可直接写 DPI 数字（如 120）。命令行 --quality 可临时覆盖这里的默认值。
QUALITY = "high"

QUALITY_PRESETS = {
    "lossless": None,   # 不压缩，图片原样嵌入（无损、体积最大）
    "high":     150,    # 电子书级，肉眼几乎无差别（推荐）
    "medium":   96,     # 屏幕清晰，体积约为 high 的 2/3
    "low":      72,     # 最省，适合只读文字
}
# ===============================================================================


def step(msg):
    print("[build_pdf] " + msg, flush=True)


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    cand = os.path.join("/opt/homebrew/bin", name)   # homebrew 兜底
    return cand if os.path.exists(cand) else name


def resolve_quality(q):
    """把画质档位名 / DPI 数字解析成 DPI 值；None 表示无损。"""
    q = str(q).strip().lower()
    if q in QUALITY_PRESETS:
        return QUALITY_PRESETS[q]
    try:
        return int(q)
    except ValueError:
        step("无效画质档位: %r（可选: %s，或直接写 DPI 数字）"
             % (q, "/".join(QUALITY_PRESETS)))
        sys.exit(1)


def resolve_bold_weight(v):
    """把加粗强度档位名 / 数字解析成 CSS font-weight 数值。

    只允许 100 的整数倍（100–900，WeasyPrint 只承认这些）或关键字
    normal/heavy。非整数倍（如 899/850/901）会被 WeasyPrint 静默忽略、
    退回默认 bold，所以这里先把它们四舍五入到最近的 100 并给出警告，
    避免再次掉进「调了字重却没变粗」的坑。
    """
    v = str(v).strip().lower()
    if v in BOLD_WEIGHT_PRESETS:
        return BOLD_WEIGHT_PRESETS[v]
    try:
        w = int(v)
    except ValueError:
        step("无效加粗强度: %r（可选: %s，或写 100 的整数倍如 700/800/900）"
             % (v, "/".join(BOLD_WEIGHT_PRESETS)))
        sys.exit(1)
    if w < 100 or w > 900:
        step("加粗强度超出范围(100–900): %r，已钳制到 900" % w)
        return 900
    if w % 100 != 0:
        rw = (w + 50) // 100 * 100      # 四舍五入到最近的 100
        rw = max(100, min(900, rw))
        step("⚠️ 加粗强度 %d 不是 100 的整数倍，WeasyPrint 会无视它；"
             "已四舍五入为 %d（本机 900=Heavy 最粗，700/800=Bold）" % (w, rw))
        return rw
    return w


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def first_chars(s, n=12):
    s = strip_tags(s)
    s = re.sub(r"\s+", "", s)        # 去空白，避免首尾/中间空格干扰
    return s[:n]


def build_label_map(md_text, html):
    """返回 {pandoc编号(int): 原始标签(str)}，按脚注定义正文回匹配。"""
    def_start = {}
    for m in re.finditer(r"\[\^([^\]]+)\]:\s*(.*)", md_text):
        def_start[m.group(1)] = first_chars(m.group(2), 12)

    mapping = {}
    for m in re.finditer(r'<li id="fn(\d+)">\s*<p>(.*?)</p>', html, re.DOTALL):
        n = int(m.group(1))
        head = first_chars(m.group(2), 12)
        lab = None
        for L, d in def_start.items():
            if d[:8] and head[:8] == d[:8]:
                lab = L
                break
        if lab is None:                       # 兜底：前 6 字匹配
            for L, d in def_start.items():
                if d[:6] and head[:6] == d[:6]:
                    lab = L
                    break
        mapping[n] = lab if lab else str(n)
    return mapping


def remap_html(html, mapping):
    used_ref = {}                             # label -> 已生成的正文引用数（处理重复引用）

    # 1) 正文引用锚点: 改 href / id / 可见数字 <sup>。
    #    同一标签被引多次时，第一个 id 用 fnrefL，后续用 fnrefL-2 / fnrefL-3 ...
    #    （避免 PDF 里出现重复锚点名，WeasyPrint 会警告 "Anchor defined twice"）。
    def repl_anchor(mm):
        n = int(mm.group(1))
        L = mapping.get(n, str(n))
        middle = mm.group(2)                  # role="doc-noteref" 等
        k = used_ref.get(L, 0) + 1
        used_ref[L] = k
        refid = "fnref%s" % L if k == 1 else "fnref%s-%d" % (L, k)
        return '<a href="#fn%s" class="footnote-ref" id="%s"%s><sup>%s</sup></a>' % (
            L, refid, middle, L)

    html = re.sub(
        r'<a href="#fn(\d+)" class="footnote-ref" id="fnref\d+"(.*?)>'
        r'<sup>\d+</sup></a>',
        repl_anchor, html)

    # 2) 脚注定义 <li id="fnN"> ... </li> : 改 id，去重，把原始编号插进第一段文字行内
    seen = set()
    li_re = re.compile(r'<li id="fn(\d+)"[^>]*>(.*?)</li>', re.DOTALL)

    def repl_li(mm):
        n = int(mm.group(1))
        L = mapping.get(n, str(n))
        inner = mm.group(2)
        if L in seen:                         # 重复脚注定义 -> 整条删除
            return ""
        seen.add(L)
        inner = re.sub(r'<p>', '<p><span class="fn-num">%s</span>' % L, inner, count=1)
        return '<li id="fn%s">%s</li>' % (L, inner)

    html = li_re.sub(repl_li, html)

    # 3) 返回链接 href="#fnrefN" -> #fnrefL（回到第一个引用处）
    def repl_back(mm):
        n = int(mm.group(1))
        L = mapping.get(n, str(n))
        return 'href="#fnref%s"' % L

    html = re.sub(r'href="#fnref(\d+)"', repl_back, html)

    # 4) 禁用脚注区 <ol> 自动编号（编号已由行内的 span 显示）。
    #    pandoc 3.x 生成的 <ol> 没有 class，class="footnotes" 在 <section> 上，
    #    所以这里用正则定位 footnotes 区里的第一个 <ol>。
    html = re.sub(
        r'(<section id="footnotes"[^>]*>)(\s*<hr\s*/?>)?\s*<ol>',
        lambda m: m.group(1) + (m.group(2) or '') +
                  '<ol class="footnotes" style="list-style:none;padding-left:0">',
        html, count=1)
    return html


def inject_css(html, font_size, footnote_ratio, line_height, max_width,
               page_size, margin, font_family, rule, p_gap, fn_gap,
               bold_weight=700):
    css = """
    body {
        font-family: %(ff)s;
        font-size: %(fs)spx;
        line-height: %(lh)s;
        max-width: %(mw)s;
        margin: 0 auto;
        padding: 0 4px;
        text-align: justify;
    }
    img { max-width: 100%%; height: auto; }
    h1, h2, h3, h4 { font-weight: bold; line-height: 1.35; }

    /* —— 加粗强度：统一覆盖所有加粗元素（标题/strong/正文彩色加粗 span）—— */
    strong, b, h1, h2, h3, h4, span[style*="font-weight"] {
        font-weight: %(bw)s !important;
    }
    p { margin: %(pg)sem 0; }
    .footnotes p { margin: %(fg)sem 0; }

    /* —— 代码块: 菈琪旭(浅黄)底色 + 潘丽宝(浓紫)前景 ——
       背景 #fffdf5→#fbf2dd 取 菈琪旭 #FABF8F 的色相但压到极淡；
       前景 #5b3a87 是 潘丽宝 #B2A1C7 加深版（原色太淡、浅黄底上对比不足）；
       装饰条用 潘丽宝 原色 #b2a1c7 做过渡，呼应前景。 */
    pre {
        background: linear-gradient(180deg, #fffdf5 0%%, #fbf2dd 100%%);
        border: 1px solid #e7d3a6;
        border-left: 4px solid #5b3a87;
        border-radius: 12px;
        padding: 14px 16px;
        color: #5b3a87;
        break-inside: avoid;
    }
    pre::before {
        content: "";
        display: block;
        height: 4px;
        border-radius: 2px;
        background: linear-gradient(90deg, #5b3a87, #b2a1c7, #5b3a87);
        margin-bottom: 10px;
    }
    pre code { background: transparent; }

    /* —— 图片标注: 居中 —— */
    figure { text-align: center; margin: 1.2em 0; }
    figcaption {
        text-align: center;
        margin-top: 0.5em;
        color: #5a6b7c;
        font-size: 0.85em;
    }
    .footnote-ref sup, sup { font-size: 0.72em; }
    .fn-num { font-weight: 700; margin-right: 0.4em; }
    .footnotes {
        font-size: %(ffs)spx;
        line-height: %(lh)s;
        margin-top: 2em;
    }
    %(rule)s
    @page { size: %(ps)s; margin: %(mg)s; }
    """ % {
        "ff": font_family,
        "fs": font_size,
        "lh": line_height,
        "mw": max_width or "none",
        "bw": bold_weight,
        "ffs": round(font_size * footnote_ratio, 2),
        "rule": "hr { margin: 1.2em 0; }" if rule else "",
        "ps": page_size,
        "mg": margin,
        "pg": p_gap,
        "fg": fn_gap,
    }
    tag = "<style>%s</style>\n</head>" % css
    if "</head>" in html:
        html = html.replace("</head>", tag, 1)
    else:
        html = "<style>%s</style>\n" % css + html
    return html


def count_pdf_links(pdf_path):
    """粗略统计 PDF 里的链接注释数（解压所有流后数 /Subtype /Link）。"""
    data = open(pdf_path, "rb").read()
    n = 0
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.DOTALL):
        try:
            blob = zlib.decompress(m.group(1))
        except Exception:
            continue
        n += blob.count(b"/Link")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", type=float, default=None,
                    help="临时覆盖正文字号 (pt)")
    ap.add_argument("--quality", default=None,
                    help="画质档位: lossless / high(150dpi) / medium(96dpi) / "
                         "low(72dpi)，或 DPI 数字如 110（默认取 CONFIG 的 QUALITY）")
    ap.add_argument("--bold", default=None,
                    help="加粗强度: normal(700) / heavy(900)，或 100 的整数倍(700/800/900)；"
                         "非整数倍会被四舍五入。默认取 CONFIG 的 BOLD_STRENGTH")
    args = ap.parse_args()

    font_size = args.font if args.font else BASE_FONT_SIZE_PT
    bold_weight = resolve_bold_weight(args.bold or BOLD_STRENGTH)

    # 画质档位 -> DPI（None = 无损）
    dpi = resolve_quality(args.quality or QUALITY)
    quality_name = "无损" if dpi is None else "%d DPI" % dpi

    if not os.path.exists(SOURCE_MD):
        step("找不到源文件: " + SOURCE_MD)
        sys.exit(1)

    pandoc = find_bin("pandoc")
    weasyprint = find_bin("weasyprint")

    tmp_html = os.path.join(HERE, "_build_tmp.html")

    # ---- 1. pandoc: md -> 独立 HTML ----
    step("pandoc 转换中 ...")
    r = subprocess.run(
        [pandoc, SOURCE_MD, "-t", "html", "-s", "--embed-resources",
         "--standalone", "-o", tmp_html],
        capture_output=True, text=True)
    if r.returncode != 0:
        step("pandoc 失败:\n" + r.stderr)
        sys.exit(1)
    for line in r.stderr.strip().splitlines():
        if "WARNING" in line:
            step("  (warn) " + line)
    html = open(tmp_html, encoding="utf-8").read()

    # ---- 2. 还原原始脚注编号 + 注入样式 ----
    step("还原脚注原始编号 (42–72) ...")
    md_text = open(SOURCE_MD, encoding="utf-8").read()
    mapping = build_label_map(md_text, html)
    step("  映射: " + ", ".join("%d->%s" % (k, mapping[k])
                                for k in sorted(mapping)))
    html = remap_html(html, mapping)

    step("注入样式 (字号 %spt, 加粗 %s) ..." % (font_size, bold_weight))
    html = inject_css(html, font_size, FOOTNOTE_FONT_RATIO,
                      LINE_HEIGHT, MAX_CONTENT_WIDTH, PAGE_SIZE, PAGE_MARGIN,
                      FONT_FAMILY, FOOTNOTE_RULE,
                      PARAGRAPH_GAP_EM, FOOTNOTE_GAP_EM, bold_weight)

    open(tmp_html, "w", encoding="utf-8").write(html)

    # ---- 3. weasyprint: HTML -> 高分辨率 PDF ----
    # 注: 图片由 weasyprint 以无损 PNG 嵌入（源为 WebP 时像素不变），体积较大，
    #     所以先输出到临时文件，下一步交给 Ghostscript 压缩。
    full_pdf = os.path.join(HERE, "_build_full.pdf")
    step("weasyprint 生成高分辨率 PDF ...")
    r = subprocess.run(
        [weasyprint, tmp_html, full_pdf],
        capture_output=True, text=True)
    if r.returncode != 0:
        step("weasyprint 失败:\n" + r.stderr)
        sys.exit(1)
    for line in r.stderr.strip().splitlines()[:12]:
        step("  (msg) " + line)

    # ---- 4. 按画质档位压缩图片（可选）----
    if dpi is None:
        step("跳过图片压缩（无损档）...")
        os.replace(full_pdf, OUTPUT_PDF)
    else:
        gs = find_bin("gs")
        step("Ghostscript 压缩图片 (<=%d DPI) ..." % dpi)
        r = subprocess.run(
            [gs, "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
             "-dDownsampleColorImages=true",
             "-dColorImageResolution=%d" % dpi,
             "-dColorImageDownsampleType=/Bicubic",
             "-dDownsampleGrayImages=true",
             "-dGrayImageResolution=%d" % dpi,
             "-dDownsampleMonoImages=true",
             "-dMonoImageResolution=600",
             "-sOutputFile=%s" % OUTPUT_PDF, full_pdf],
            capture_output=True, text=True)
        if r.returncode != 0:
            step("Ghostscript 失败:\n" + r.stderr)
            sys.exit(1)
        os.remove(full_pdf)

    if os.path.exists(OUTPUT_PDF):
        size = os.path.getsize(OUTPUT_PDF)
        step("完成 -> %s  (%.2f MB, 画质档位 %s)"
             % (OUTPUT_PDF, size / 1024 / 1024, quality_name))
        try:
            n_links = count_pdf_links(OUTPUT_PDF)
            step("PDF 内可点击链接数: %d（脚注跳转 + 返回）" % n_links)
        except Exception:
            pass
    else:
        step("未生成 PDF，请检查 weasyprint 报错。")
        sys.exit(1)

    try:
        os.remove(tmp_html)
    except OSError:
        pass


if __name__ == "__main__":
    main()
