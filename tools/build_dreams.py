"""สร้างหน้าทำนายฝันฉบับขยาย แก้ชื่อหน้าที่ภาษาแปลก และลบกล่อง "พื้นที่โฆษณา" ที่ว่างเปล่า
รันจากโฟลเดอร์หลักของเว็บ:  python3 tools/build_dreams.py
"""
import html, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from dreams_a import DREAMS_A
from dreams_b import DREAMS_B

ROOT = pathlib.Path(__file__).resolve().parent.parent
DREAM = ROOT / "dream"
CONTENT = {**DREAMS_A, **DREAMS_B}

def load_txt(path):
    """อ่านไฟล์ dreams_more_*.txt (รูปแบบอธิบายไว้บรรทัดแรกของไฟล์)"""
    out, cur = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("# "):
            continue
        if line.startswith("## "):
            num, verdict, summary = line[3:].split("|", 2)
            cur = out[num.strip()] = dict(verdict=verdict.strip(), summary=summary.strip(), variants=[])
        elif line.startswith("v: "):
            t, x = line[3:].split("|", 1)
            cur["variants"].append((t.strip(), x.strip()))
        elif line[:3] in ("L: ", "W: ", "A: "):
            cur[{"L": "love", "W": "work", "A": "advice"}[line[0]]] = line[3:].strip()
    return out

for _p in sorted(pathlib.Path(__file__).parent.glob("dreams_more_*.txt")):
    for _k, _v in load_txt(_p).items():
        assert _k not in CONTENT, _k
        CONTENT[_k] = _v

# ชื่อหน้าที่ภาษาแปลก -> ชื่อที่คนค้นจริง (ลิงก์เดิมใช้ได้เหมือนเดิม)
RENAME = {
    "005": "ฝันเห็นคนตาย", "008": "ฝันว่าท้อง", "009": "ฝันว่าบินได้",
    "014": "ฝันเห็นงานแต่งงาน", "019": "ฝันว่าสอบ", "020": "ฝันว่าตกจากที่สูง",
    "068": "ฝันเห็นแฟนเก่า", "080": "ฝันว่าร้องไห้", "081": "ฝันว่าหัวเราะ",
    "098": "ฝันว่าไหว้พระ", "099": "ฝันว่าทะเลาะ", "100": "ฝันว่าวิ่ง",
    "101": "ฝันว่าว่ายน้ำ", "102": "ฝันว่าหลงทาง",
}
for k, v in CONTENT.items():
    if "name" in v:
        RENAME.setdefault(k, v["name"])

AD_BOX = re.compile(r'<div class="ad"><!-- วางโค้ดโฆษณาตรงนี้ -->พื้นที่โฆษณา</div>\s*')
H1_RE = re.compile(r"<h1>(.*?) ทำนายฝัน แปลว่าอะไร</h1>")

def current_names():
    names = {}
    for f in sorted(DREAM.glob("[0-9][0-9][0-9].html")):
        m = H1_RE.search(f.read_text(encoding="utf-8"))
        if m:
            names[f.stem] = m.group(1)
    return names

OLD = current_names()
NEW = {k: RENAME.get(k, v) for k, v in OLD.items()}
BY_NAME = {v: k for k, v in NEW.items()}
for k, v in CONTENT.items():
    v.setdefault("name", NEW[k])

def esc(s):
    return html.escape(s, quote=True)

def link_refs(text):
    """แปลง 'อ่านต่อที่หน้า <ชื่อ>' เป็นลิงก์ไปหน้านั้น"""
    m = re.search(r"อ่านต่อที่หน้า (\S+)$", text)
    if not m or m.group(1) not in BY_NAME:
        return esc(text)
    name = m.group(1)
    head = text[: m.start()].rstrip()
    out = (esc(head) + " ") if head else ""
    return out + f'อ่านต่อที่หน้า <a href="{BY_NAME[name]}">{esc(name)}</a>'

def numbers_of(src):
    m = re.search(r'<b>เลขเด่น:</b> <span class="tag">([^<]+)</span>', src)
    return m.group(1).strip() if m else ""

def build_main(num, d, nums):
    n = d["name"]
    parts = [
        f"<h1>{esc(n)} ทำนายฝัน แปลว่าอะไร</h1>",
        '<div class="box">',
        f"<p>{esc(d['summary'])}</p>",
        f'<p><b>ดีหรือร้าย:</b> <span class="tag">{esc(d["verdict"])}</span> '
        f'<b>เลขเด่น:</b> <span class="tag">{esc(nums)}</span></p>',
        "</div>",
        f'<div class="box"><h2>{esc(n)}แบบต่าง ๆ แปลว่าอะไร</h2>',
    ]
    for title, text in d["variants"]:
        parts.append(f"<h3>{esc(title)}</h3><p>{link_refs(text)}</p>")
    parts.append("</div>")
    parts.append(
        f'<div class="box"><h2>{esc(n)} ความหมายด้านความรักและการงาน</h2>'
        f"<p><b>ความรัก:</b> {esc(d['love'])}</p>"
        f"<p><b>การงานและการเงิน:</b> {esc(d['work'])}</p></div>"
    )
    parts.append(
        f'<div class="box"><h2>คำแนะนำเมื่อ{esc(n)}</h2><p>{esc(d["advice"])}</p>'
        f"<p>เลขเด่นที่ตำรานิยมใช้คู่กับความฝันนี้คือ {esc(nums)} เป็นเพียงความเชื่อเพื่อความบันเทิง</p></div>"
    )
    return "\n".join(parts)

changed = 0
for f in sorted(DREAM.glob("[0-9][0-9][0-9].html")):
    num = f.stem
    src = f.read_text(encoding="utf-8")
    out = AD_BOX.sub("", src)
    nums = numbers_of(src)
    new_name = NEW.get(num)
    old_name = OLD.get(num)

    if num in CONTENT:
        d = CONTENT[num]
        start = out.index("<h1>")
        end = out.index('<div class="box"><h2>วิธีอ่านคำทำนายฝัน</h2>')
        out = out[:start] + build_main(num, d, nums) + "\n" + out[end:]
        desc = d["summary"]
        if len(desc) > 150:
            desc = desc[:148].rsplit(" ", 1)[0] + "…"
        out = re.sub(r'<meta name="description" content="[^"]*">',
                     f'<meta name="description" content="{esc(desc)} เลขเด่น {esc(nums)}">', out, count=1)
    elif new_name != old_name:
        out = out.replace(f"<h1>{old_name} ทำนายฝัน", f"<h1>{new_name} ทำนายฝัน", 1)
        out = out.replace(f'content="{old_name} ', f'content="{new_name} ', 1)

    if new_name != old_name or num in CONTENT:
        out = re.sub(r"<title>.*?</title>",
                     f"<title>{esc(new_name)} แปลว่าอะไร ทำนายฝัน เลขเด่น {esc(nums)}</title>", out, count=1)
    if '<link rel="canonical"' not in out:
        out = out.replace('<link rel="stylesheet"',
                          f'<link rel="canonical" href="https://duangjai.site/dream/{num}"><link rel="stylesheet"', 1)
    # อัปเดตชื่อลิงก์ไปหน้าอื่นที่เปลี่ยนชื่อ
    for k, nn in NEW.items():
        if OLD[k] != nn:
            out = out.replace(f'href="{k}">{OLD[k]}<', f'href="{k}">{nn}<')
    if out != src:
        f.write_text(out, encoding="utf-8")
        changed += 1

# หน้ารวมคำทำนายฝันและหน้าอื่นที่ลิงก์มา
for f in [DREAM / "index.html", *ROOT.glob("*.html"), *(ROOT / "articles").glob("*.html")]:
    src = f.read_text(encoding="utf-8")
    out = AD_BOX.sub("", src)
    for k, nn in NEW.items():
        if OLD[k] != nn:
            out = re.sub(rf'(href="(?:\.\./)?(?:dream/)?{k}">){re.escape(OLD[k])}<', rf"\g<1>{nn}<", out)
    if out != src:
        f.write_text(out, encoding="utf-8")
        changed += 1

css = ROOT / "style.css"
c = css.read_text(encoding="utf-8")
if "h3{" not in c:
    css.write_text(c + "\nh3{font-size:1.02rem;margin:.9em 0 .2em}\n", encoding="utf-8")

print("files changed:", changed)
