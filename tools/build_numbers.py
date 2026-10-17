"""สร้างหน้าความหมายเลขคู่ 00–99 (/number/00 ... /number/99) และหน้ารวม /number/
ความหมายคู่เลขดึงจากตาราง P ในหน้า lucky-number.html เพื่อให้ตรงกับเครื่องเช็กเบอร์
รันจากโฟลเดอร์หลักของเว็บ:  python3 tools/build_numbers.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "number"
OUT.mkdir(exist_ok=True)
SRC = (ROOT / "lucky-number.html").read_text(encoding="utf-8")
P = json.loads(re.search(r"const P = (\{.*?\});", SRC, re.S).group(1))
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7389759760990204" crossorigin="anonymous"></script>'

# ความหมายเลขเดี่ยวตามดาวประจำเลขในศาสตร์เลขไทย
DIGIT = {
    "0": ("ศูนย์", "ความว่าง การเริ่มต้นใหม่ และแรงที่ยังไม่มีทิศทาง"),
    "1": ("ดาวอาทิตย์", "ความเป็นผู้นำ ความมั่นใจ และเกียรติยศ"),
    "2": ("ดาวจันทร์", "อารมณ์ ความอ่อนโยน และเสน่ห์"),
    "3": ("ดาวอังคาร", "ความกล้า พลังงาน และความใจร้อน"),
    "4": ("ดาวพุธ", "สติปัญญา การพูด และการค้าขาย"),
    "5": ("ดาวพฤหัสบดี", "คุณธรรม ความรู้ และผู้ใหญ่อุปถัมภ์"),
    "6": ("ดาวศุกร์", "ความรัก ความสวยงาม และเงินทอง"),
    "7": ("ดาวเสาร์", "ความอดทน ภาระ และอุปสรรค"),
    "8": ("ดาวราหู", "ความทะเยอทะยาน การเสี่ยง และสิ่งที่ไม่คาดคิด"),
    "9": ("ดาวเกตุ", "สิ่งศักดิ์สิทธิ์ ลางสังหรณ์ และปัญญาญาณ"),
}
GRADE = {"g": ("เลขดี", "ดี"), "n": ("เลขกลาง", "ปานกลาง"), "b": ("เลขควรเลี่ยง", "ควรเลี่ยง")}
TAG = {"m": "การเงิน", "w": "การงาน", "l": "ความรัก", "h": "โชคและสุขภาพใจ"}
ADVICE = {
    "g": "ถ้าเบอร์โทรศัพท์ ทะเบียนรถ หรือบ้านเลขที่ของคุณมีคู่เลขนี้ ถือว่าเป็นคู่ที่ช่วยเสริม ยิ่งอยู่ตำแหน่งท้ายของเบอร์ ตำราว่ายิ่งส่งผลชัด",
    "n": "คู่เลขนี้มีทั้งด้านดีและด้านที่ต้องระวัง ถ้าในเบอร์มีคู่เลขดีอยู่ร่วมด้วย จะช่วยถ่วงให้สมดุล ไม่จำเป็นต้องเปลี่ยนเบอร์เพราะคู่นี้คู่เดียว",
    "b": "ตำราเลขศาสตร์มักแนะนำให้เลี่ยงคู่นี้ โดยเฉพาะตำแหน่งท้ายเบอร์ ถ้าเบอร์ที่ใช้อยู่มีคู่นี้ ไม่ต้องกังวลจนเกินไป ลองดูภาพรวมทั้งเบอร์ด้วยเครื่องเช็กเบอร์มงคลก่อนตัดสินใจ",
}

def esc(s):
    return html.escape(s, quote=True)

def info(pair):
    key = "".join(sorted(pair))
    return P[key]

GOOD = sorted({p for p in (f"{i:02d}" for i in range(100)) if info(p)[0] == "g"})

def page(pair):
    g, tags, text = info(pair)
    a, b = pair[0], pair[1]
    rev = b + a
    gname, gshort = GRADE[g]
    aspects = " ".join(TAG[t] for t in tags)
    title = f"ความหมายเลข {pair} เลข{gshort}ไหม เบอร์มงคล ทะเบียนรถ บ้านเลขที่"
    desc = f"เลข {pair} {text} ({gname}) ดูความหมายคู่เลข {pair} สำหรับเบอร์โทร ทะเบียนรถ และบ้านเลขที่"
    same = [p for p in GOOD if p != pair and set(info(p)[1]) & set(tags)][:8] if g == "g" and tags else GOOD[:8]
    body = [
        f'<p class="nav"><a href="../">🔮 ดวงใจ</a> · <a href="./">ความหมายเลขคู่</a> · <a href="../lucky-number">เช็กเบอร์มงคล</a></p>',
        f"<h1>ความหมายเลข {pair}</h1>",
        '<div class="box">',
        f"<p>เลข {pair} ในศาสตร์เลขมงคลไทย หมายถึง{esc(text)}</p>",
        f'<p><b>ระดับ:</b> <span class="tag">{gname}</span>'
        + (f' <b>เด่นด้าน:</b> <span class="tag">{esc(aspects)}</span>' if aspects else "")
        + "</p></div>",
        f'<div class="box"><h2>เลข {esc(a)} กับเลข {esc(b)} มาจากอะไร</h2>',
        f"<p>เลข {a} ตรงกับ{DIGIT[a][0]} หมายถึง{DIGIT[a][1]}</p>",
        (f"<p>เลข {b} ตรงกับ{DIGIT[b][0]} หมายถึง{DIGIT[b][1]}</p>" if b != a
         else f"<p>เมื่อเลข {a} มาคู่กัน พลังของ{DIGIT[a][0]}จะซ้ำกันสองเท่า ทั้งด้านดีและด้านที่ต้องระวัง</p>"),
        f"<p>เมื่อสองเลขมาอยู่คู่กันเป็น {pair} พลังทั้งสองผสมกัน จึงให้ความหมายรวมตามที่อธิบายไว้ด้านบน</p></div>",
        f'<div class="box"><h2>เลข {pair} ในเบอร์โทร ทะเบียนรถ และบ้านเลขที่</h2>',
        f"<p>{esc(ADVICE[g])}</p>",
    ]
    if rev != pair:
        body.append(f'<p>เลข {pair} กับ <a href="{rev}">เลข {rev}</a> ใช้ความหมายเดียวกัน เพราะเป็นคู่เลขเดียวกันสลับตำแหน่ง</p>')
    body.append("</div>")
    body.append('<div class="box"><h2>เช็กเบอร์ของคุณทั้งเบอร์</h2>'
                '<p>หนึ่งเบอร์มีหลายคู่เลข ความหมายรวมจึงสำคัญกว่าคู่เดียว ลองใช้เครื่องมือฟรีด้านล่างดูคะแนนรวมทั้งเบอร์</p>'
                '<p><a class="tag" href="../lucky-number">เช็กเบอร์โทรศัพท์</a> <a class="tag" href="../lucky-plate">เช็กทะเบียนรถ</a> '
                '<a class="tag" href="../lucky-house">เช็กบ้านเลขที่</a></p></div>')
    body.append('<div class="box"><h2>คู่เลขดีอื่น ๆ</h2><p>'
                + " ".join(f'<a class="tag" href="{p}">{p}</a>' for p in same)
                + '</p><p><a href="./">ดูความหมายเลขคู่ทั้งหมด 00–99</a></p></div>')
    body.append('<p class="note"><a href="../about">เกี่ยวกับเรา</a> · <a href="../privacy">นโยบายความเป็นส่วนตัว</a> · '
                '<a href="../contact">ติดต่อเรา</a><br>ความหมายตามความเชื่อเลขศาสตร์ เพื่อความบันเทิงเท่านั้น</p>')
    return (f'<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">{ADS}'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
            f'<meta name="description" content="{esc(desc)}">'
            f'<link rel="canonical" href="https://duangjai.site/number/{pair}"><link rel="stylesheet" href="../style.css">'
            f'</head><body><div class="w">' + "\n".join(body) + "</div></body></html>")

def index():
    rows = []
    for g in ("g", "n", "b"):
        ps = [f"{i:02d}" for i in range(100) if info(f"{i:02d}")[0] == g]
        rows.append(f'<div class="box"><h2>{GRADE[g][0]} ({len(ps)} คู่)</h2><p>'
                    + " ".join(f'<a class="tag" href="{p}">{p}</a>' for p in ps) + "</p></div>")
    body = ('<p class="nav"><a href="../">🔮 ดวงใจ</a> · <a href="../lucky-number">เช็กเบอร์มงคล</a></p>'
            "<h1>ความหมายเลขคู่ 00–99</h1>"
            '<div class="box"><p>รวมความหมายเลขคู่ทั้ง 100 คู่ตามศาสตร์เลขมงคลไทย ใช้ดูเบอร์โทรศัพท์ ทะเบียนรถ และบ้านเลขที่ '
            'กดที่เลขเพื่ออ่านความหมายเต็ม หรือ <a href="../lucky-number">เช็กเบอร์ทั้งเบอร์ฟรี</a></p></div>'
            + "".join(rows)
            + '<p class="note"><a href="../about">เกี่ยวกับเรา</a> · <a href="../privacy">นโยบายความเป็นส่วนตัว</a> · '
              '<a href="../contact">ติดต่อเรา</a><br>ความหมายตามความเชื่อเลขศาสตร์ เพื่อความบันเทิงเท่านั้น</p>')
    return (f'<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">{ADS}'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            "<title>ความหมายเลขคู่ 00–99 เลขมงคล เลขเสีย สำหรับเบอร์โทร ทะเบียนรถ</title>"
            '<meta name="description" content="รวมความหมายเลขคู่ 00 ถึง 99 แยกเลขดี เลขกลาง เลขควรเลี่ยง ใช้ดูเบอร์โทรศัพท์ ทะเบียนรถ บ้านเลขที่">'
            '<link rel="canonical" href="https://duangjai.site/number/"><link rel="stylesheet" href="../style.css">'
            f'</head><body><div class="w">{body}</div></body></html>')

for i in range(100):
    p = f"{i:02d}"
    (OUT / f"{p}.html").write_text(page(p), encoding="utf-8")
(OUT / "index.html").write_text(index(), encoding="utf-8")

# sitemap: เพิ่มหน้าเลขคู่ (ถ้ายังไม่มี)
sm = ROOT / "sitemap.xml"
s = sm.read_text(encoding="utf-8")
if "/number/" not in s:
    urls = ["https://duangjai.site/number/"] + [f"https://duangjai.site/number/{i:02d}" for i in range(100)]
    add = "".join(f"<url><loc>{u}</loc></url>\n" for u in urls)
    s = s.replace("</urlset>", add + "</urlset>")
    sm.write_text(s, encoding="utf-8")
print("number pages: 100 + index")
