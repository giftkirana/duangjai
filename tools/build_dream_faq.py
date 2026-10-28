"""เพิ่มคำถามที่พบบ่อย (พร้อม FAQPage schema) ให้หน้าทำนายฝันทุกหน้า
และเนื้อหาเพิ่มเติมให้หน้ายอดนิยม (ข้อมูลใน dream_extra.py)
รันซ้ำได้ ถ้ารัน build_dreams.py ใหม่ ให้รันไฟล์นี้ต่อทุกครั้ง:  python3 tools/build_dream_faq.py
"""
import html, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from dream_extra import X

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANCHOR = '<div class="box"><h2>วิธีอ่านคำทำนายฝัน</h2>'
BLOCK = re.compile(r"<!--faq-->.*?<!--/faq-->\n?", re.S)
LD = re.compile(r'<script type="application/ld\+json" id="faq">.*?</script>', re.S)
esc = lambda s: html.escape(s, quote=True)
txt = lambda s: re.sub(r"<[^>]+>", "", html.unescape(s)).strip()

n = 0
for f in sorted((ROOT / "dream").glob("[0-9][0-9][0-9].html")):
    s = f.read_text(encoding="utf-8")
    s = LD.sub("", BLOCK.sub("", s))
    name = re.search(r"<h1>(.*?) ทำนายฝัน", s).group(1)
    summary = txt(re.search(r'<div class="box">\s*<p>(.*?)</p>', s, re.S).group(1))
    verdict = txt(re.search(r'<b>ดีหรือร้าย:</b> <span class="tag">(.*?)</span>', s).group(1))
    nums = txt(re.search(r'<b>เลขเด่น:</b> <span class="tag">(.*?)</span>', s).group(1))
    love = re.search(r"<b>ความรัก:</b> (.*?)</p>", s)
    work = re.search(r"<b>การงานและการเงิน:</b> (.*?)</p>", s)
    faq = [(f"{name} ดีหรือร้าย", f"ตามตำราทำนายฝันไทย {name}ถือว่า{verdict} {summary}"),
           (f"{name} เลขเด่นอะไร", f"เลขเด่นที่ตำรานิยมใช้คู่กับ{name}คือ {nums} เป็นความเชื่อเพื่อความบันเทิง")]
    if love:
        faq.append((f"{name} เกี่ยวกับความรักไหม", txt(love.group(1))))
    if work:
        faq.append((f"{name} เกี่ยวกับการงานและการเงินอย่างไร", txt(work.group(1))))
    parts = ["<!--faq-->"]
    x = X.get(f.stem)
    if x:
        parts.append(f'<div class="box"><h2>{esc(name)}แบบอื่นที่คนค้นบ่อย</h2>'
                     + "".join(f"<h3>{esc(t)}</h3><p>{esc(d)}</p>" for t, d in x["more"]) + "</div>")
        parts.append(f'<div class="box"><h2>ทำไมถึง{esc(name)}</h2><p>{esc(x["why"])}</p></div>')
        parts.append(f'<div class="box"><h2>{esc(name)} ความหมายตามสถานะ</h2>'
                     + "".join(f"<p><b>{esc(t)}:</b> {esc(d)}</p>" for t, d in x["who"]) + "</div>")
    parts.append('<div class="box"><h2>คำถามที่พบบ่อย</h2>'
                 + "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in faq) + "</div>")
    parts.append("<!--/faq-->\n")
    assert ANCHOR in s, f
    s = s.replace(ANCHOR, "\n".join(parts) + ANCHOR, 1)
    ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        ensure_ascii=False).replace("</", "<\\/")
    s = s.replace("</head>", f'<script type="application/ld+json" id="faq">{ld}</script></head>', 1)
    f.write_text(s, encoding="utf-8")
    n += 1
print("dream pages:", n, "extra:", len(X))
