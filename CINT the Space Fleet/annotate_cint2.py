# -*- coding: utf-8 -*-
import re

# 章节专属标注引擎：把 2.md 里每句台词和“我”包成带 data-char 的 <span>。
# 运行: python3 annotate_cint2.py   (就地重写 2.md，并生成 annotation_report.txt 供核对)
#
# 注意：本文件顶部只定义“配色与加粗表 REG”和纯函数，主流程放在 main() 里、
# 并用 if __name__ == "__main__" 守卫。这样 recolor.py 可以安全地
#   import annotate_cint2 as _cfg; COLOR = _cfg.REG
# 读取唯一配色源，而不会因为 import 就重新跑一遍标注。
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(_HERE, "2.md")
OUT = os.path.join(_HERE, "2.md")
REPORT = os.path.join(_HERE, "annotation_report.txt")

REG = {
 "ithea":     {"names":["艾瑟雅"], "gender":"f", "color":"E36C0A", "bold":True},
 "nasania": {"names":["纳萨尼亚"], "gender":"f", "color":None, "bold":False},
 "elba":   {"names":["爱尔贝"], "gender":"f", "color":None, "bold":False},
 "lillia":    {"names":["莉莉娅","莉莉"], "gender":"f", "color":"FF0000", "bold":False},
 "rhantolk":  {"names":["兰朵露可","兰"], "gender":"f", "color":"8DB3E2", "bold":True},
 "chtholly":  {"names":["珂朵莉"], "gender":"f", "color":"548DD4", "bold":True},
 "tiat":      {"names":["缇亚忒","缇亚"], "gender":"f", "color":"92D050", "bold":False},
 "lakhesh":   {"names":["菈琪旭","菈琪"], "gender":"f", "color":"FABF8F", "bold":False},
 "nephren":   {"names":["奈芙莲"], "gender":"f", "color":"7030A0", "bold":False},
 "pannibal":  {"names":["潘丽宝"], "gender":"f", "color":"B2A1C7", "bold":False},
 "nopht":     {"names":["诺夫特"], "gender":"f", "color":"FF3300", "bold":True},
 "collon":    {"names":["可蓉"], "gender":"f", "color":"FFC0CB", "bold":False},
 "almita":    {"names":["阿尔弥塔"], "gender":"f", "color":"F5E6C4", "bold":True},
 "eudea":     {"names":["优蒂亚"], "gender":"f", "color":"4E7CA1", "bold":False},
 "marguerite":{"names":["玛尔歌莉特","玛尔歌"], "gender":"f", "color":"8D6E63", "bold":False},
 "feodor":    {"names":["费奥多尔"], "gender":"m", "color":"455A64", "bold":False},
 "willem":    {"names":["威廉"], "gender":"m", "color":None, "bold":True},
 "suowong":   {"names":["史旺"], "gender":"m", "color":"5D4037", "bold":False},
 "limeskin":  {"names":["灰岩皮"], "gender":"m", "color":"76923C", "bold":False},
 "instructor":{"names":["教官"], "gender":"m", "color":"546E7A", "bold":False},
 "moaning":   {"names":["摩尔宁"], "gender":"n", "color":None, "bold":False},
}
NAME2ID = {}
for _id, d in REG.items():
    for nm in sorted(d["names"], key=len, reverse=True):
        NAME2ID[nm] = _id
ALL_NAMES = sorted(NAME2ID.keys(), key=len, reverse=True)
PRONS = ["我","你","他","她"]
SENT = "。！？…"  # sentence-ending punctuation that breaks attribution

def strip_quotes(s):
    return re.sub(r"「[^」]*」", "", s)

def focal_id(lineno):
    if 1650 <= lineno <= 1753: return "nasania"   # dream = 纳萨尼亚 memory
    if 740  <= lineno <= 857:  return "lakhesh"      # 菈琪旭 视角
    if 1232 <= lineno <= 1343: return "pannibal"     # 潘丽宝 潜入/登陆
    if 1456 <= lineno <= 1577: return "tiat"         # 缇亚忒 战场
    if 724  <= lineno <= 731:  return "almita"       # 游戏间 (与优蒂亚对)
    if 1090 <= lineno <= 1145: return "almita"       # 游戏间 (阿尔弥塔主视角："优蒂亚和我""她转方向，我踩击发")
    if 1368 <= lineno <= 1403: return "almita"       # 游戏间 (与优蒂亚对)
    return "ithea"

def rightmost_token(s):
    """rightmost NAME/PRON such that nothing in SENT between it and end of s, gap<=40"""
    best=None; bp=None
    for nm in ALL_NAMES:
        for m in re.finditer(re.escape(nm), s):
            seg = s[m.end():]
            if SENT not in seg and len(seg)<=40:
                if bp is None or m.start()>bp: bp=m.start(); best=nm
    for pr in PRONS:
        for m in re.finditer(re.escape(pr), s):
            seg=s[m.end():]
            if SENT not in seg and len(seg)<=40:
                if bp is None or m.start()>bp: bp=m.start(); best=pr
    return best

def leftmost_token(s):
    best=None; bp=None
    for nm in ALL_NAMES:
        for m in re.finditer(re.escape(nm), s):
            seg=s[:m.start()]
            if SENT not in seg and len(seg)<=40:
                if bp is None or m.start()<bp: bp=m.start(); best=nm
    for pr in PRONS:
        for m in re.finditer(re.escape(pr), s):
            seg=s[:m.start()]
            if SENT not in seg and len(seg)<=40:
                if bp is None or m.start()<bp: bp=m.start(); best=pr
    return best

def resolve_token(tok, lineno, buf):
    if tok == "我": return focal_id(lineno)
    if tok in NAME2ID: return NAME2ID[tok]
    if tok == "她":
        for cid in reversed(buf):
            if REG[cid]["gender"] in ("f","n"): return cid
        return None
    if tok == "他":
        for cid in reversed(buf):
            if REG[cid]["gender"] == "m": return cid
        return None
    if tok == "你": return focal_id(lineno)
    return None

def wrap(text, cid):
    if cid is None: return text
    d = REG[cid]
    style=""
    if d["color"]: style+="color:#%s;"%d["color"]
    if d["bold"]: style+="font-weight:bold;"
    if style: return '<span style="%s" data-char="%s">%s</span>'%(style,cid,text)
    return '<span data-char="%s">%s</span>'% (cid,text)

FIRST_PERSON = {"ithea","nasania","almita","yutia"}
def wrap_me(s, cid):
    if cid not in FIRST_PERSON:
        return s
    out=[];i=0;n=len(s);depth=0;buf=""
    while i<n:
        c=s[i]
        if c=='<' and s[i:i+5]=='<span':
            if buf: out.append(buf); buf=""
            j=s.find('>',i); out.append(s[i:j+1]); i=j+1; depth+=1; continue
        if c=='<' and s[i:i+7]=='</span>':
            if buf: out.append(buf); buf=""
            j=s.find('>',i); out.append(s[i:j+1]); i=j+1; depth-=1; continue
        if c=='我' and depth==0:
            if buf: out.append(buf); buf=""
            out.append(wrap('我',cid)); i+=1; continue
        buf+=c; i+=1
    if buf: out.append(buf)
    return "".join(out)

def main():
    with open(SRC, encoding="utf-8") as f:
        raw=f.read()
    # 先剥离已有的 <span> 标注，保证重复运行幂等、且不嵌套
    raw = re.sub(r"</?span[^>]*>", "", raw)
    lines=raw.split("\n")
    N=len(lines)
    out=[]; report=[]; unknown=0
    buf=[]; last_speaker=None; scene_partner=None; cur_focal=None; in_fence=False

    def is_skip(l):
        x=l.strip()
        return x.startswith("```") or x.startswith("#") or x=="" or set(x)<=set("-")

    def neighbor_lone_name(lineno, idx):
        for d in (-3,-2,-1,1,2,3):
            j=idx+d
            if 0<=j<N and not is_skip(lines[j]):
                cl=strip_quotes(lines[j])
                no={}
                for nm in ALL_NAMES:
                    if nm in cl: no[NAME2ID[nm]]=no.get(NAME2ID[nm],0)+cl.count(nm)
                if len(no)==1: return list(no)[0]
        return None

    for idx in range(N):
        lineno=idx+1; line=lines[idx]
        if is_skip(line):
            if line.strip().startswith("```"): in_fence=not in_fence
            out.append(line); continue
        if in_fence:
            out.append(line); continue
        focal=focal_id(lineno)
        if focal!=cur_focal:
            cur_focal=focal; last_speaker=None; scene_partner=None
        # buf update (names only)
        clean=strip_quotes(line)
        for nm in ALL_NAMES:
            if nm in clean: buf.append(NAME2ID[nm])
        if len(buf)>40: buf=buf[-40:]
        # quotes
        quotes=[]; k=0; n=len(line)
        while k<n:
            if line[k]=='「':
                e=line.find('」',k)
                if e==-1: e=n-1
                quotes.append((k,e)); k=e+1
            else: k+=1
        if not quotes:
            out.append(wrap_me(line, focal)); continue
        # resolve line speaker
        speaker=None
        cands=[]
        for (a,b) in quotes:
            before=strip_quotes(line[:a]); after=strip_quotes(line[b+1:])
            t=rightmost_token(before)
            if t: cands.append(t)
            t2=leftmost_token(after)
            if t2: cands.append(t2)
        for tok in cands:
            cid=resolve_token(tok,lineno,buf)
            if cid: speaker=cid; break
        if speaker is None:
            no={}
            for nm in ALL_NAMES:
                if nm in clean: no[NAME2ID[nm]]=no.get(NAME2ID[nm],0)+clean.count(nm)
            if len(no)==1: speaker=list(no)[0]
        # 摩尔宁 / 机械孩子 encounter: only 圣剑摩尔宁（制导核心）本身开口才算 moaning；
        # 兽孩子的台词（"一起玩吗？"等）与缇亚忒的日志备注（"此处有孩子"）不标注
        if speaker is None and 1484 <= lineno <= 1577:
            neigh=" ".join(lines[max(0,idx-3):idx+4])
            if ("制导核心" in neigh) or ("报错" in neigh) or ("cuda" in neigh):
                speaker="moaning"
        # 教官 (training AI) referenced as 小窗口 / 训练体, or explicit 教官说
        if speaker is None:
            neigh=" ".join(lines[max(0,idx-3):idx+4])
            if ("小窗口" in neigh) or ("训练体" in neigh) or ("教官说" in neigh):
                speaker="instructor"
        if speaker is None:
            if last_speaker is None:
                nb=neighbor_lone_name(lineno,idx)
                speaker=nb if nb else focal
            else:
                if scene_partner and scene_partner!=focal and last_speaker in (focal, scene_partner):
                    if last_speaker==focal: speaker=scene_partner
                    else: speaker=focal
                else:
                    speaker=focal
        if speaker=="unknown": unknown+=1
        if speaker not in (None,"unknown",focal):
            scene_partner=speaker
        last_speaker=speaker
        # build line with each quote wrapped
        res=[]; prev=0
        for (a,b) in quotes:
            res.append(line[prev:a])
            content=line[a+1:b]
            res.append("「"+wrap(content,speaker)+"」")
            prev=b+1
            report.append("L%-4d -> %-10s | 「%s」"%(lineno, speaker if speaker else "?", content[:38]))
        res.append(line[prev:])
        out.append(wrap_me("".join(res), focal))

    with open(OUT,"w",encoding="utf-8") as f: f.write("\n".join(out))
    with open(REPORT,"w",encoding="utf-8") as f: f.write("\n".join(report))
    print("quotes:",len(report),"unknown:",unknown)

if __name__ == "__main__":
    main()
