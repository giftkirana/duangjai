"""สร้างหน้าชื่อมงคล (ทักษา) และหน้า "เขาคิดยังไงกับเรา"
- lucky-name.html        เครื่องเช็กชื่อมงคลตามวันเกิด
- name/index.html        หลักการตั้งชื่อมงคล + ลิงก์ทุกวันเกิด
- name/<day>.html        ชื่อมงคลคนเกิดแต่ละวัน (8 หน้า) กรองชื่อที่ไม่มีอักษรกาลกิณีให้อัตโนมัติ
- feel.html              สุ่มว่าคนที่นึกถึงรู้สึกยังไงกับเรา
รันจากโฟลเดอร์หลักของเว็บ:  python3 tools/build_names.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "name"
OUT.mkdir(exist_ok=True)
SITE = "https://duangjai.site"
ADS = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7389759760990204" crossorigin="anonymous"></script>'

def esc(s):
    return html.escape(s, quote=True)

# ---------------- ทักษา ----------------
VOWELS = "ะาำิีึืุูเแโใไัฤฦ"
GROUP = {  # ดาว: อักษร
    "sun": "อ" + VOWELS, "mon": "กขฃคฅฆง", "tue": "จฉชซฌญ", "wed": "ฎฏฐฑฒณ",
    "sat": "ดตถทธน", "thu": "บปผฝพฟภม", "rahu": "ยรลว", "fri": "ศษสหฬฮ",
}
GROUP_SHOW = {  # ใช้แสดงผล (สระแสดงเป็นคำว่า "สระทุกตัว")
    "sun": "สระทุกตัว และ อ", "mon": "ก ข ค ฆ ง", "tue": "จ ฉ ช ซ ฌ ญ", "wed": "ฎ ฏ ฐ ฑ ฒ ณ",
    "sat": "ด ต ถ ท ธ น", "thu": "บ ป ผ ฝ พ ฟ ภ ม", "rahu": "ย ร ล ว", "fri": "ศ ษ ส ห ฬ ฮ",
}
WHEEL = ["sun", "mon", "tue", "wed", "sat", "thu", "rahu", "fri"]
POS = ["บริวาร", "อายุ", "เดช", "ศรี", "มูละ", "อุตสาหะ", "มนตรี", "กาลกิณี"]
POS_MEAN = {
    "บริวาร": "คนรอบข้าง ครอบครัว ลูกน้อง และเพื่อนที่คอยช่วยเหลือ",
    "อายุ": "สุขภาพแข็งแรง อายุยืน ชีวิตราบรื่น",
    "เดช": "อำนาจ ความน่าเกรงขาม ชื่อเสียง และความสำเร็จในหน้าที่การงาน",
    "ศรี": "สิริมงคล โชคลาภ เงินทอง และเสน่ห์",
    "มูละ": "หลักฐานมั่นคง ทรัพย์สิน มรดก และที่ดิน",
    "อุตสาหะ": "ความขยัน อดทน และความพยายามที่นำไปสู่ความสำเร็จ",
    "มนตรี": "ผู้ใหญ่อุปถัมภ์ มีคนคอยสนับสนุนและให้คำแนะนำ",
    "กาลกิณี": "สิ่งอัปมงคล อุปสรรค ตำราแนะนำให้เลี่ยงอักษรกลุ่มนี้ในชื่อ",
}
DAYS = [  # slug, ชื่อวัน, ดาวเริ่ม
    ("sunday", "วันอาทิตย์", "sun"), ("monday", "วันจันทร์", "mon"), ("tuesday", "วันอังคาร", "tue"),
    ("wednesday", "วันพุธ (กลางวัน)", "wed"), ("wednesday-night", "วันพุธ (กลางคืน)", "rahu"),
    ("thursday", "วันพฤหัสบดี", "thu"), ("friday", "วันศุกร์", "fri"), ("saturday", "วันเสาร์", "sat"),
]

def layout(start):
    i = WHEEL.index(start)
    return {POS[k]: WHEEL[(i + k) % 8] for k in range(8)}

def planet_of(ch):
    for p, letters in GROUP.items():
        if ch in letters:
            return p
    return None

def bad_name(name, start):
    """ชื่อมีอักษรกาลกิณีไหม (นับพยัญชนะและตัว อ; คนเกิดวันจันทร์เลี่ยงชื่อขึ้นต้นด้วยสระด้วย)"""
    kal = layout(start)["กาลกิณี"]
    for ch in name:
        if ch in VOWELS:
            continue
        if planet_of(ch) == kal:
            return True
    if kal == "sun" and name[0] in "เแโใไ":
        return True
    return False

def has_pos(name, start, pos):
    p = layout(start)[pos]
    return any(planet_of(ch) == p for ch in name if ch not in VOWELS)

# ---------------- ชื่อพร้อมความหมาย ----------------
BOYS = [
    ("กิตติ", "เกียรติ ชื่อเสียง"), ("กิตติพงษ์", "เชื้อสายผู้มีเกียรติ"), ("ณัฐวุฒิ", "นักปราชญ์ผู้มีความเจริญ"),
    ("ณัฐพล", "นักปราชญ์ผู้มีกำลัง"), ("ธนกร", "ผู้สร้างทรัพย์"), ("ธนพล", "ผู้มีกำลังทรัพย์"),
    ("ธนวัฒน์", "ผู้เจริญด้วยทรัพย์"), ("ธีรเดช", "นักปราชญ์ผู้มีอำนาจ"), ("ธีรภัทร", "นักปราชญ์ผู้เจริญ"),
    ("ภูมิ", "แผ่นดิน"), ("ภูริ", "ผู้มีปัญญากว้างขวาง"), ("ภานุ", "พระอาทิตย์ แสงสว่าง"),
    ("ปกรณ์", "ตำรา คัมภีร์"), ("ปภังกร", "ผู้สร้างแสงสว่าง"), ("พีรพล", "ผู้มีกำลังกล้าแข็ง"),
    ("พงศกร", "ผู้สร้างวงศ์ตระกูล"), ("ศุภกร", "ผู้สร้างความดีงาม"), ("ศิวกร", "ผู้สร้างความสุขและความดีงาม"),
    ("ศักดิ์ชัย", "ผู้มีอำนาจและชัยชนะ"), ("อนันต์", "ไม่มีที่สิ้นสุด"), ("อธิป", "ผู้เป็นใหญ่"),
    ("วรเมธ", "ผู้มีปัญญาประเสริฐ"), ("วรวุฒิ", "ผู้มีความเจริญอันประเสริฐ"), ("วชิระ", "เพชร สายฟ้า"),
    ("ชยพล", "กำลังแห่งชัยชนะ"), ("ชัยวัฒน์", "ผู้เจริญด้วยชัยชนะ"), ("เตชินท์", "ผู้เป็นใหญ่ด้วยเดช"),
    ("นที", "แม่น้ำ"), ("ภาคิน", "ผู้มีโชค มีส่วนแห่งความดี"), ("กันตพงศ์", "เชื้อสายผู้เป็นที่รัก"),
    ("เมธัส", "ผู้มีปัญญา"), ("กวิน", "ผู้เป็นกวี ผู้มีความรู้"), ("ภัทร", "ความเจริญ ความดีงาม"),
    ("ณภัทร", "ผู้มีความรู้และความเจริญ"), ("ราชันย์", "ผู้เป็นใหญ่ ราชา"), ("ทินกร", "พระอาทิตย์"),
    ("คณิน", "ผู้มีหมู่คณะ มีพวกพ้อง"), ("ธราธร", "ผู้ค้ำจุนแผ่นดิน"), ("ยศพล", "ผู้มีกำลังแห่งยศ"),
    ("ลาภิน", "ผู้มีลาภ"), ("สิรวิชญ์", "นักปราชญ์ผู้มีสิริมงคล"), ("ปัณณวิชญ์", "นักปราชญ์ผู้มีปัญญา"),
    ("กฤตภาส", "ผู้สร้างแสงสว่าง"), ("ภูวเดช", "ผู้มีอำนาจเหนือแผ่นดิน"), ("ณัฐนนท์", "นักปราชญ์ผู้มีความสุข"),
    ("พุฒิพงศ์", "เชื้อสายผู้มีปัญญา"), ("ชนาธิป", "ผู้เป็นใหญ่ในหมู่ชน"), ("ตะวัน", "พระอาทิตย์"),
    ("ปุณณวัฒน์", "ผู้เจริญอย่างเต็มเปี่ยม"), ("รัชพล", "ผู้มีกำลังแห่งความเป็นใหญ่"),
]
GIRLS = [
    ("กมลชนก", "ผู้เกิดจากดอกบัว"), ("กัญญา", "หญิงสาว"), ("กานต์ธิดา", "ลูกสาวผู้เป็นที่รัก"),
    ("กนกพร", "พรอันมีค่าดั่งทอง"), ("ขวัญข้าว", "ขวัญแห่งความอุดมสมบูรณ์"), ("จิราพร", "พรอันยั่งยืน"),
    ("ชนิกานต์", "ผู้เป็นที่รักของหมู่ชน"), ("ชุติมา", "ผู้มีความรุ่งเรือง"), ("ณัฐชา", "ผู้เกิดมาเป็นนักปราชญ์"),
    ("ณัฐธิดา", "ลูกสาวผู้เป็นนักปราชญ์"), ("ธนพร", "พรแห่งทรัพย์"), ("ธิดารัตน์", "ลูกสาวผู้ประเสริฐดั่งแก้ว"),
    ("ธัญญา", "ผู้มีโชค ความอุดมสมบูรณ์"), ("นภา", "ท้องฟ้า"), ("นันทนา", "ความยินดี ความเพลิดเพลิน"),
    ("นวพร", "พรใหม่"), ("ปวีณา", "ผู้ฉลาด เชี่ยวชาญ"), ("ปิยะดา", "ผู้เป็นที่รัก"),
    ("ปาริชาต", "ดอกไม้สวรรค์"), ("ปัณฑิตา", "ผู้รู้ ผู้มีปัญญา"), ("พรรณี", "ผู้มีผิวพรรณงาม"),
    ("พิชชา", "ความรู้"), ("ภัทรา", "ผู้เจริญ ดีงาม"), ("มนัสนันท์", "ผู้มีใจยินดี"),
    ("มณีรัตน์", "แก้วมณี"), ("เมธาวี", "ผู้มีปัญญา"), ("ยุพา", "หญิงสาว"),
    ("รัตนา", "แก้ว ของมีค่า"), ("รุ่งทิพย์", "แสงอรุณอันเป็นทิพย์"), ("ลลิตา", "ผู้งดงาม น่ารัก"),
    ("วรรณา", "ผิวพรรณงาม"), ("วรัญญา", "ผู้มีปัญญาประเสริฐ"), ("วิมลรัตน์", "แก้วอันบริสุทธิ์"),
    ("ศศิธร", "พระจันทร์"), ("ศิริพร", "พรอันเป็นสิริมงคล"), ("สิริกานต์", "ผู้เป็นที่รักและมีมงคล"),
    ("สุพิชญา", "ผู้มีปัญญาดี"), ("สุชาดา", "ผู้เกิดดี"), ("อรอุมา", "หญิงงามดั่งพระอุมา"),
    ("อรนุช", "น้องสาวผู้งดงาม"), ("อัญชลี", "การประนมมือไหว้"), ("อาภัสรา", "ผู้มีรัศมีสว่าง"),
    ("จันทร์เพ็ญ", "พระจันทร์เต็มดวง"), ("เบญญา", "ปัญญา"), ("ณิชาภัทร", "ผู้มีความรู้และความเจริญ"),
    ("ภัคจิรา", "ผู้มีโชคยั่งยืน"), ("ธนัชชา", "ผู้เกิดมาพร้อมทรัพย์"), ("พิมพ์ลดา", "เถาวัลย์ผู้งดงาม"),
    ("ปุณยวีร์", "ผู้กล้าหาญในทางบุญ"), ("กชพร", "พรอันงามดั่งดอกบัว"),
]

# ---------------- ส่วนหัว/ท้ายหน้า ----------------
CSS = """<style>
input,select{width:100%;padding:12px;border-radius:10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);font:inherit}
label{display:block;margin:10px 0 4px;color:var(--mute);font-size:.9rem}
.btn{display:block;width:100%;margin-top:14px;background:var(--acc);color:#fff;border:0;border-radius:10px;padding:12px 20px;font:inherit;font-size:1.05rem;cursor:pointer;text-align:center;text-decoration:none}
.sub{text-align:center;color:var(--mute);margin:0 0 10px}h1{text-align:center}
table{width:100%;border-collapse:collapse;font-size:.93rem}td,th{padding:7px 6px;border-top:1px solid var(--line);vertical-align:top;text-align:left}th{color:var(--mute);font-weight:600}
.k{background:#fde8e8;color:#a33}.s{background:#e4f6e9;color:#1d6b3a}
@media (prefers-color-scheme:dark){.k{background:#4a1f26;color:#ffadad}.s{background:#16422a;color:#8fe3ad}}
.nm{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.nm div{border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:var(--bg)}.nm b{display:block;font-size:1.05rem}.nm span{color:var(--mute);font-size:.86rem}
.nm i{font-style:normal;font-size:.75rem;color:var(--gold)}
.share{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:center;margin:12px 0 4px}.share .lbl{width:100%;text-align:center;color:var(--mute);font-size:.9rem}
.sh{display:inline-block;padding:8px 16px;border-radius:10px;font:inherit;font-size:.95rem;text-decoration:none;border:0;cursor:pointer;color:#fff}
.sh.line{background:#06c755}.sh.fb{background:#1877f2}.sh.cp{background:var(--mute)}
[hidden]{display:none!important}
</style>"""

FOOTER = ('<p class="note"><a href="{r}">หน้าแรก</a> · <a href="{r}lucky-name">เช็กชื่อมงคล</a> · <a href="{r}name/">ชื่อมงคลตามวันเกิด</a> · '
          '<a href="{r}feel">เขาคิดยังไงกับเรา</a> · <a href="{r}lucky-number">เบอร์มงคล</a><br>'
          '<a href="{r}articles/">บทความ</a> · <a href="{r}dream/">คำทำนายฝันทั้งหมด</a> · <a href="{r}daily/">ดวงรายวัน</a> · '
          '<a href="{r}about">เกี่ยวกับเรา</a> · <a href="{r}privacy">นโยบายความเป็นส่วนตัว</a> · <a href="{r}contact">ติดต่อเรา</a><br>'
          'เพื่อความบันเทิงและเป็นแนวทางตามความเชื่อเท่านั้น</p>')

SHARE_JS = """function shareBox(el,txt,url,label){
 const line='https://social-plugins.line.me/lineit/share?url='+encodeURIComponent(url)+'&text='+encodeURIComponent(txt);
 const fb='https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url);
 el.insertAdjacentHTML('beforeend',`<div class="share"><span class="lbl">${label}</span><a class="sh line" href="${line}" target="_blank" rel="noopener">LINE</a><a class="sh fb" href="${fb}" target="_blank" rel="noopener">Facebook</a><button class="sh cp" type="button">คัดลอกผล</button></div>`);
 el.querySelector('.cp').onclick=async e=>{const b=e.currentTarget;
  try{await navigator.clipboard.writeText(txt);b.textContent='คัดลอกแล้ว'}catch(_){b.textContent='คัดลอกไม่ได้'}
  setTimeout(()=>b.textContent='คัดลอกผล',1800)};
}"""

def page(path, title, desc, body, r, og_title=None):
    url = f"{SITE}/{path}"
    return (f'<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">{ADS}'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="ดวงใจ">'
            f'<meta property="og:title" content="{esc(og_title or title)}"><meta property="og:description" content="{esc(desc)}">'
            f'<meta property="og:url" content="{url}"><meta property="og:locale" content="th_TH">'
            f'<link rel="canonical" href="{url}"><link rel="stylesheet" href="{r}style.css">{CSS}</head>'
            f'<body><div class="w">{body}{FOOTER.format(r=r)}</div></body></html>')

def nav(r, here):
    return (f'<p class="nav"><a href="{r}">🔮 ดวงใจ</a> · <a href="{r}lucky-name">เช็กชื่อมงคล</a> · '
            f'<a href="{r}name/">ชื่อมงคลตามวันเกิด</a> · <a href="{r}feel">เขาคิดยังไงกับเรา</a></p>')

def day_table(start, r=""):
    lay = layout(start)
    rows = []
    for pos in POS:
        cls = ' class="k"' if pos == "กาลกิณี" else (' class="s"' if pos in ("เดช", "ศรี", "มนตรี") else "")
        rows.append(f"<tr{cls}><td><b>{pos}</b></td><td>{GROUP_SHOW[lay[pos]]}</td><td>{POS_MEAN[pos]}</td></tr>")
    return '<table><tr><th>ภูมิ</th><th>อักษร</th><th>ความหมาย</th></tr>' + "".join(rows) + "</table>"

def names_grid(lst, start):
    out = []
    for n, m in lst:
        if bad_name(n, start):
            continue
        tags = [p for p in ("ศรี", "เดช", "มนตรี") if has_pos(n, start, p)]
        t = f'<i>มีอักษร{" ".join(tags)}</i>' if tags else ""
        out.append(f"<div><b>{esc(n)}</b><span>{esc(m)}</span>{t}</div>")
    return out

# ---------------- หน้าชื่อมงคลแต่ละวัน ----------------
def day_page(slug, dname, start):
    lay = layout(start)
    boys = names_grid(BOYS, start)
    girls = names_grid(GIRLS, start)
    kal = GROUP_SHOW[lay["กาลกิณี"]]
    good = " · ".join(f"{p}: {GROUP_SHOW[lay[p]]}" for p in ("ศรี", "เดช", "มนตรี"))
    mon_note = ("<p>สำหรับคนเกิดวันจันทร์ ตำราถือว่าสระเป็นกาลกิณี แต่ชื่อภาษาไทยเลี่ยงสระทั้งหมดไม่ได้ "
                "ผู้ตั้งชื่อส่วนใหญ่จึงเลี่ยงตัว อ และชื่อที่ขึ้นต้นด้วยสระ เช่น เ แ โ ใ ไ เป็นหลัก รายชื่อด้านล่างกรองตามหลักนี้แล้ว</p>"
                if start == "mon" else "")
    others = " ".join(f'<a class="tag" href="{s}">{d}</a>' for s, d, _ in DAYS if s != slug)
    body = (nav("../", slug)
            + f"<h1>ชื่อมงคลคนเกิด{dname}</h1>"
            + f'<p class="sub">อักษรกาลกิณีที่ควรเลี่ยง และรายชื่อมงคลผู้ชาย ผู้หญิง พร้อมความหมาย</p>'
            + f'<div class="box"><p style="margin-top:0">คนเกิด{dname} <b>อักษรกาลกิณี</b> คือ <b>{kal}</b> ไม่ควรมีในชื่อ</p>'
            + f"<p style=\"margin-bottom:0\">อักษรที่ส่งเสริม {good}</p>{mon_note}</div>"
            + f'<div class="box"><h2 style="margin-top:0">ทักษาคนเกิด{dname}</h2>{day_table(start)}</div>'
            + f'<div class="box"><h2 style="margin-top:0">ชื่อมงคลผู้ชาย คนเกิด{dname} ({len(boys)} ชื่อ)</h2><div class="nm">{"".join(boys)}</div></div>'
            + f'<div class="box"><h2 style="margin-top:0">ชื่อมงคลผู้หญิง คนเกิด{dname} ({len(girls)} ชื่อ)</h2><div class="nm">{"".join(girls)}</div></div>'
            + '<div class="box"><h2 style="margin-top:0">เช็กชื่อของคุณเอง</h2><p>มีชื่อในใจอยู่แล้ว พิมพ์ชื่อและเลือกวันเกิด '
              'เครื่องจะบอกทีละตัวอักษรว่าอยู่ในภูมิไหน มีอักษรกาลกิณีหรือไม่</p>'
              f'<a class="btn" href="../lucky-name?day={slug}">เช็กชื่อมงคลฟรี</a></div>'
            + f'<div class="box"><h2 style="margin-top:0">ชื่อมงคลวันเกิดอื่น</h2><p>{others}</p></div>')
    title = f"ชื่อมงคลคนเกิด{dname} ผู้ชาย ผู้หญิง อักษรกาลกิณี ตั้งชื่อลูก"
    desc = f"ชื่อมงคลสำหรับคนเกิด{dname} อักษรกาลกิณีคือ {kal} รวมชื่อผู้ชาย {len(boys)} ชื่อ ชื่อผู้หญิง {len(girls)} ชื่อ พร้อมความหมาย ไม่มีอักษรกาลกิณี"
    return page(f"name/{slug}", title, desc, body, "../")

def name_index():
    rows = "".join(f'<tr><td><a href="{s}"><b>{d}</b></a></td><td>{GROUP_SHOW[layout(st)["กาลกิณี"]]}</td>'
                   f'<td>{GROUP_SHOW[layout(st)["ศรี"]]}</td></tr>' for s, d, st in DAYS)
    groups = "".join(f"<tr><td><b>{n}</b></td><td>{GROUP_SHOW[p]}</td></tr>" for n, p in (
        ("วรรคที่ 1 (ดาวอาทิตย์)", "sun"), ("วรรคที่ 2 (ดาวจันทร์)", "mon"), ("วรรคที่ 3 (ดาวอังคาร)", "tue"),
        ("วรรคที่ 4 (ดาวพุธ)", "wed"), ("วรรคที่ 5 (ดาวเสาร์)", "sat"), ("วรรคที่ 6 (ดาวพฤหัสบดี)", "thu"),
        ("วรรคที่ 7 (ดาวราหู)", "rahu"), ("วรรคที่ 8 (ดาวศุกร์)", "fri")))
    pos = "".join(f"<tr><td><b>{p}</b></td><td>{POS_MEAN[p]}</td></tr>" for p in POS)
    body = (nav("../", "idx")
            + "<h1>ตั้งชื่อมงคลตามวันเกิด</h1>"
            + '<p class="sub">หลักทักษาแบบเข้าใจง่าย อักษรกาลกิณีของแต่ละวัน และรายชื่อมงคลพร้อมความหมาย</p>'
            + '<div class="box"><h2 style="margin-top:0">เลือกวันเกิด</h2><table><tr><th>วันเกิด</th><th>อักษรกาลกิณี (ควรเลี่ยง)</th><th>อักษรศรี (เสริมโชค)</th></tr>'
            + rows + "</table></div>"
            + '<div class="box"><h2 style="margin-top:0">ตั้งชื่อมงคลด้วยหลักทักษาคืออะไร</h2>'
              "<p>ทักษาเป็นตำราโหราศาสตร์ไทยที่แบ่งตัวอักษรเป็น 8 กลุ่มตามดาวประจำวัน แล้ววางเรียงเป็นวงกลม 8 ตำแหน่ง เรียกว่าภูมิ "
              "ตำแหน่งแรกเริ่มที่ดาวประจำวันเกิดของเจ้าของชื่อ แล้วนับต่อไปตามลำดับ ภูมิแต่ละตำแหน่งให้ความหมายต่างกัน "
              "ชื่อที่ดีควรมีอักษรในภูมิที่เป็นมงคล และไม่มีอักษรในภูมิกาลกิณี</p>"
              "<p>หลักที่ผู้ตั้งชื่อส่วนใหญ่ใช้</p><ul>"
              "<li>ไม่มีอักษรกาลกิณีของวันเกิดในชื่อ (บางตำราใช้กับนามสกุลด้วย)</li>"
              "<li>มีอักษรในภูมิศรี เดช หรือมนตรี อย่างน้อยหนึ่งตัว เพื่อเสริมโชค อำนาจ และผู้อุปถัมภ์</li>"
              "<li>ความหมายของชื่อดี อ่านง่าย และเจ้าของชื่อชอบ</li>"
              "<li>ถ้าเกิดวันพุธ ให้ดูเวลาเกิด ก่อน 18:00 นับเป็นพุธกลางวัน หลัง 18:00 นับเป็นพุธกลางคืน (ราหู)</li></ul></div>"
            + f'<div class="box"><h2 style="margin-top:0">อักษร 8 วรรค</h2><table>{groups}</table></div>'
            + f'<div class="box"><h2 style="margin-top:0">ความหมายของภูมิทั้ง 8</h2><table>{pos}</table></div>'
            + '<div class="box"><h2 style="margin-top:0">เช็กชื่อของคุณ</h2><p>พิมพ์ชื่อ เลือกวันเกิด แล้วดูว่าแต่ละตัวอักษรอยู่ในภูมิไหน</p>'
              '<a class="btn" href="../lucky-name">เช็กชื่อมงคลฟรี</a></div>')
    title = "ตั้งชื่อมงคลตามวันเกิด หลักทักษา อักษรกาลกิณี 7 วัน พร้อมรายชื่อมงคล"
    desc = "วิธีตั้งชื่อมงคลตามวันเกิดด้วยหลักทักษา ตารางอักษรกาลกิณีและอักษรศรีของทุกวัน ความหมายภูมิทั้ง 8 พร้อมรายชื่อมงคลผู้ชายผู้หญิง"
    return page("name/", title, desc, body, "../")

# ---------------- เครื่องเช็กชื่อมงคล ----------------
def checker():
    data = json.dumps({"G": GROUP, "W": WHEEL, "P": POS, "M": POS_MEAN, "V": VOWELS,
                       "D": [[s, d, st] for s, d, st in DAYS]}, ensure_ascii=False)
    opts = "".join(f'<option value="{s}">{d}</option>' for s, d, _ in DAYS)
    body = (nav("", "chk")
            + "<h1>✍️ เช็กชื่อมงคล</h1>"
            + '<p class="sub">ดูว่าชื่อของคุณมีอักษรกาลกิณีไหม และแต่ละตัวอักษรเสริมด้านใด ตามหลักทักษา</p>'
            + '<div class="box"><label for="nm">ชื่อ (ภาษาไทย)</label><input id="nm" placeholder="เช่น ธนพร" autocomplete="off">'
              '<label for="sn">นามสกุล (ไม่บังคับ)</label><input id="sn" placeholder="ไม่ต้องใส่ก็ได้" autocomplete="off">'
              f'<label for="dy">วันเกิด</label><select id="dy"><option value="">– เลือกวันเกิด –</option>{opts}</select>'
              '<button class="btn" id="go">เช็กชื่อ</button><p id="err" style="color:#d64545;margin:8px 0 0" hidden></p></div>'
            + '<div id="res" hidden></div>'
            + '<div class="box"><h2 style="margin-top:0">อ่านผลยังไง</h2><p>ทักษาแบ่งตัวอักษรเป็น 8 กลุ่มตามดาว แล้วจัดเป็น 8 ภูมิตามวันเกิด '
              'ชื่อที่ดีควร <b>ไม่มีอักษรกาลกิณี</b> และมีอักษรใน <b>ภูมิศรี เดช หรือมนตรี</b> อย่างน้อยหนึ่งตัว '
              'เครื่องนี้นับพยัญชนะและตัว อ เป็นหลัก ส่วนสระจะแสดงให้ดูประกอบ เพราะชื่อภาษาไทยเลี่ยงสระไม่ได้</p>'
              '<p style="margin-bottom:0">อยากได้ชื่อใหม่ ดู <a href="name/">รายชื่อมงคลตามวันเกิด</a> ที่กรองอักษรกาลกิณีไว้ให้แล้ว</p></div>'
            + """<style>.ch{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:6px 0 12px}
.ch span{min-width:3.6em;text-align:center;border:1px solid var(--line);border-radius:10px;padding:4px 6px;background:var(--bg);line-height:1.3}
.ch b{display:block;font-size:1.4rem}.ch small{font-size:.72rem;color:var(--mute)}
.ch span.k{border-color:#e5a3a3}.ch span.s{border-color:#9fd5b0}
.vd{text-align:center;font-size:1.25rem;font-weight:700;color:var(--gold);margin:4px 0}</style>"""
            + f"<script>const T={data};\n{SHARE_JS}\n" + r"""
const $=id=>document.getElementById(id);
const planet=ch=>{for(const p in T.G)if(T.G[p].includes(ch))return p;return null};
function layout(start){const i=T.W.indexOf(start),o={};T.P.forEach((p,k)=>o[T.W[(i+k)%8]]=p);return o}
const q=new URLSearchParams(location.search);if(q.get('day'))$('dy').value=q.get('day');
function run(){
 const nm=$('nm').value.replace(/\s+/g,''),sn=$('sn').value.replace(/\s+/g,''),dy=$('dy').value,err=$('err');
 if(!/[ก-ฮ]/.test(nm)){err.textContent='พิมพ์ชื่อเป็นภาษาไทยก่อนนะ';err.hidden=false;return}
 if(!dy){err.textContent='เลือกวันเกิดด้วยนะ';err.hidden=false;return}
 err.hidden=true;
 const day=T.D.find(d=>d[0]===dy),lay=layout(day[2]);
 const cnt={};T.P.forEach(p=>cnt[p]=0);
 function chips(word,countIt){return [...word].map(ch=>{const p=planet(ch);if(!p)return '';
   const pos=lay[p],isV=T.V.includes(ch);if(countIt&&!isV)cnt[pos]++;
   const cls=pos==='กาลกิณี'&&!isV?'k':(['ศรี','เดช','มนตรี'].includes(pos)&&!isV?'s':'');
   return `<span class="${cls}"><b>${ch}</b><small>${isV?'สระ':pos}</small></span>`}).join('')}
 const c1=chips(nm,true);const kName=cnt['กาลกิณี'];
 const before={...cnt};const c2=sn?chips(sn,true):'';const kSur=cnt['กาลกิณี']-kName;
 const startV=lay['sun']==='กาลกิณี'&&/^[เแโใไ]/.test(nm);
 const goodPos=['ศรี','เดช','มนตรี'].filter(p=>before[p]>0);
 let verdict,note;
 if(kName||startV){verdict='ชื่อนี้มีอักษรกาลกิณี';note=`ตามตำรา คนเกิด${day[1]}ควรเลี่ยงอักษร${kName?'กาลกิณีที่ทำเครื่องหมายสีแดง':''}${startV?' และชื่อที่ขึ้นต้นด้วยสระ':''} ถ้าคิดจะเปลี่ยนชื่อ ลองดูรายชื่อมงคลด้านล่าง ถ้าไม่เปลี่ยน ก็ไม่ต้องกังวลจนเกินไป ชื่อเป็นเพียงส่วนหนึ่งของชีวิต`}
 else if(goodPos.length){verdict='ชื่อมงคล ✨';note=`ไม่มีอักษรกาลกิณี และมีอักษรภูมิ${goodPos.join(' ')} ช่วยเสริม`+goodPos.map(p=>` ${p}: ${T.M[p]}`).join(' ·')}
 else{verdict='ชื่อใช้ได้ ไม่มีอักษรกาลกิณี';note='ชื่อนี้ไม่มีอักษรกาลกิณี แต่ยังไม่มีอักษรภูมิศรี เดช หรือมนตรี ถ้าอยากเสริมดวง ลองเลือกชื่อเล่นที่มีอักษรกลุ่มนี้'}
 const det=T.P.filter(p=>before[p]>0&&p!=='กาลกิณี').map(p=>`<li><b>${p}</b> (${before[p]} ตัว) ${T.M[p]}</li>`).join('');
 const res=$('res');
 res.innerHTML=`<div class="box"><p class="vd">${verdict}</p><div class="ch">${c1}</div>
 ${sn?`<p style="text-align:center;margin:0;color:var(--mute);font-size:.9rem">นามสกุล</p><div class="ch">${c2}</div>`:''}
 <p>${note}</p>${sn&&kSur?`<p>นามสกุลมีอักษรกาลกิณี ${kSur} ตัว ส่วนใหญ่นามสกุลเปลี่ยนไม่ได้ ตำราจึงให้น้ำหนักที่ชื่อตัวมากกว่า</p>`:''}
 ${det?`<p style="margin-bottom:4px"><b>ชื่อนี้เสริมด้าน</b></p><ul style="margin-top:0">${det}</ul>`:''}
 <a class="btn" href="name/${dy}">ดูชื่อมงคลคนเกิด${day[1]}</a></div>`;
 res.hidden=false;
 const txt=`ชื่อ ${nm} คนเกิด${day[1]}: ${verdict}\nลองเช็กชื่อของคุณที่ https://duangjai.site/lucky-name`;
 shareBox(res.firstElementChild,txt,'https://duangjai.site/lucky-name','แชร์ผลให้เพื่อนหรือครอบครัว');
 res.scrollIntoView({behavior:'smooth',block:'start'});
}
$('go').onclick=run;['nm','sn'].forEach(id=>$(id).addEventListener('keydown',e=>{if(e.key==='Enter')run()}));
</script>""")
    title = "เช็กชื่อมงคล ตามวันเกิด ฟรี ดูอักษรกาลกิณี หลักทักษา – ดวงใจ"
    desc = "เช็กชื่อมงคลฟรี พิมพ์ชื่อและวันเกิด ดูทีละตัวอักษรว่าอยู่ภูมิไหน มีอักษรกาลกิณีหรือไม่ ชื่อเสริมด้านศรี เดช มนตรี ตามหลักทักษา"
    return page("lucky-name", title, desc, body, "")

# ---------------- เขาคิดยังไงกับเรา ----------------
FEEL = {
    "levels": [
        [90, 99, "คิดถึงคุณอยู่บ่อย ๆ", [
            "ช่วงนี้คุณอยู่ในความคิดของเขามากกว่าที่คุณคิด เวลาเห็นอะไรที่เกี่ยวกับคุณ เขาจะนึกถึงคุณขึ้นมาทันที",
            "เขาให้ความสำคัญกับคุณเป็นพิเศษ แค่ยังเลือกวิธีแสดงออกไม่ถูก บางครั้งจึงดูเหมือนนิ่ง ๆ ทั้งที่ข้างในไม่ใช่",
            "พลังความรู้สึกของเขาที่ส่งมาหาคุณค่อนข้างแรง เขารู้สึกสบายใจทุกครั้งที่ได้คุยหรืออยู่ใกล้คุณ"]],
        [78, 89, "มีใจให้ แต่ยังไม่กล้าแสดงออก", [
            "เขารู้สึกดีกับคุณจริง แต่กลัวว่าถ้าแสดงออกมากไป ความสัมพันธ์ตอนนี้จะเปลี่ยน",
            "เขาแอบสังเกตคุณอยู่ไม่น้อย จำเรื่องเล็ก ๆ ที่คุณเคยเล่าได้ แต่ยังรอจังหวะที่มั่นใจกว่านี้",
            "ในใจเขามีคุณอยู่ แต่ยังมีเรื่องบางอย่างในชีวิตที่ทำให้เขาลังเลที่จะก้าวเข้ามาเร็ว"]],
        [65, 77, "รู้สึกดี และอยากใกล้ชิดมากขึ้น", [
            "เขาชอบพลังงานของคุณ อยู่ด้วยแล้วสบายใจ และอยากรู้จักคุณมากขึ้นอีกหน่อย",
            "เขามองคุณเป็นคนพิเศษคนหนึ่ง ความรู้สึกกำลังค่อย ๆ เติบโต ถ้ามีโอกาสได้คุยกันบ่อยขึ้น จะชัดเจนเร็วขึ้น",
            "เขาเปิดใจให้คุณมากกว่าคนทั่วไป แค่ยังไม่แน่ใจว่าคุณรู้สึกแบบเดียวกันหรือเปล่า"]],
        [50, 64, "ยังสับสนกับความรู้สึกตัวเอง", [
            "ใจเขายังแกว่งไปมา บางวันรู้สึกใกล้ บางวันรู้สึกไกล เพราะเขาเองก็ยังไม่แน่ใจว่าต้องการอะไร",
            "เขามีความรู้สึกดีให้คุณ แต่ยังมีเรื่องงาน ครอบครัว หรือเรื่องเก่าในใจที่ทำให้คิดได้ไม่สุด",
            "เขากำลังชั่งใจอยู่ ถ้าคุณชัดเจนกับเขามากขึ้นอีกนิด เขาจะตัดสินใจได้ง่ายขึ้น"]],
        [38, 49, "มองคุณเป็นคนสำคัญแบบคนสนิท", [
            "ตอนนี้เขามองคุณเป็นคนที่ไว้ใจและสบายใจด้วย เหมือนคนสนิทมากกว่าความรักแบบหวือหวา",
            "เขาเห็นคุณค่าของคุณและอยากให้คุณอยู่ในชีวิต แต่ความรู้สึกแบบคนรักยังไม่ชัดในตอนนี้",
            "เขารู้สึกปลอดภัยเวลาอยู่กับคุณ ความสัมพันธ์แบบนี้ค่อย ๆ เปลี่ยนได้ ถ้าให้เวลา"]],
        [25, 37, "ยุ่งกับชีวิตตัวเอง ยังไม่ได้คิดเรื่องนี้", [
            "ช่วงนี้เขามีเรื่องให้คิดเยอะ เรื่องความรู้สึกถูกวางไว้ก่อน ไม่ได้แปลว่าเขาไม่สนใจคุณเลย",
            "พลังของเขาตอนนี้มุ่งไปที่งานหรือปัญหาส่วนตัว คุณอาจรู้สึกว่าเขาห่าง แต่เป็นเรื่องของจังหวะมากกว่า",
            "เขายังไม่พร้อมเปิดใจให้ใครเต็มที่ในช่วงนี้ ลองดูแลหัวใจตัวเองให้ดีก่อน"]],
    ],
    "unsaid": [
        "อยากชวนคุณไปไหนสักที่ แต่ยังไม่กล้าเอ่ยปาก", "อยากรู้ว่าคุณคิดยังไงกับเขาบ้าง",
        "ขอบคุณที่คุณเคยอยู่ข้าง ๆ ในวันที่เขาเหนื่อย", "อยากคุยกับคุณนานกว่านี้ แต่กลัวว่าคุณจะรำคาญ",
        "แอบดีใจทุกครั้งที่คุณทักมาก่อน", "อยากขอโทษเรื่องที่เคยทำให้คุณไม่สบายใจ",
        "รู้สึกว่าคุณเข้าใจเขามากกว่าคนอื่น", "อยากเห็นคุณมีความสุข ไม่ว่าจะเป็นแบบไหน",
        "กลัวว่าถ้าพูดออกไป จะเสียความสัมพันธ์ที่มีอยู่", "คิดถึงช่วงเวลาที่เคยหัวเราะด้วยกัน",
    ],
    "signs": [
        "เขาจะทักหรือส่งอะไรบางอย่างมาหาคุณแบบไม่มีเหตุผลชัดเจน", "เขาจะจำเรื่องเล็ก ๆ ที่คุณพูดได้ และหยิบมาคุยต่อ",
        "คุณจะเห็นเขาโผล่มาดูสตอรี่หรือโพสต์ของคุณบ่อยขึ้น", "เขาจะหาเรื่องคุยต่อ แม้บทสนทนาควรจบแล้ว",
        "เขาจะถามถึงคุณกับคนรอบข้าง", "เขาจะชวนทำกิจกรรมที่ได้อยู่ด้วยกันนานขึ้น",
        "เขาจะตอบข้อความคุณเร็วกว่าปกติ", "เขาจะเล่าเรื่องส่วนตัวให้ฟังมากขึ้น",
    ],
    "advice": {
        "crush": ["ลองเริ่มบทสนทนาด้วยเรื่องที่เขาสนใจ จะช่วยให้เขากล้าเปิดใจมากขึ้น",
                  "อย่ารีบเร่ง ให้ความสัมพันธ์ค่อย ๆ เติบโต แต่แสดงให้เขาเห็นว่าคุณใส่ใจ",
                  "ลองชวนทำกิจกรรมสบาย ๆ ด้วยกัน จะได้เห็นความรู้สึกจริงของเขาชัดขึ้น"],
        "talking": ["ถ้าคุยกันมาสักพักแล้ว ลองชวนเจอกันจริง ๆ จะรู้ใจกันเร็วขึ้น",
                    "สื่อสารให้ชัดว่าคุณรู้สึกยังไง จะช่วยลดความไม่แน่ใจของทั้งสองฝ่าย",
                    "อย่าเก็บทุกคำตอบของเขามาคิดมาก จังหวะชีวิตแต่ละคนไม่เท่ากัน"],
        "partner": ["หาเวลาคุยกันแบบไม่มีมือถือ จะช่วยให้ใจกลับมาใกล้กัน",
                    "บอกขอบคุณในเรื่องเล็ก ๆ ที่เขาทำให้ จะเติมความรู้สึกดีให้กันได้มาก",
                    "ถ้ามีเรื่องค้างใจ คุยกันตรง ๆ ด้วยน้ำเสียงอ่อนโยน ดีกว่าเก็บไว้"],
        "ex": ["ถามใจตัวเองให้ชัดก่อนว่าอยากกลับไป หรือแค่คิดถึงความทรงจำ",
               "ถ้าจะติดต่อกลับ ให้เริ่มแบบเบา ๆ และเคารพคำตอบของเขา",
               "ดูแลตัวเองให้มีความสุขก่อน ไม่ว่าคำตอบจะเป็นอย่างไร คุณจะพร้อมกว่าเดิม"],
        "friend": ["ความสัมพันธ์แบบเพื่อนที่ดีเป็นพื้นฐานที่แข็งแรง ค่อย ๆ ใช้เวลาด้วยกันมากขึ้น",
                   "สังเกตว่าเขาปฏิบัติกับคุณต่างจากเพื่อนคนอื่นไหม จะช่วยให้คุณเห็นคำตอบ",
                   "อย่ากดดันตัวเองให้ต้องรู้คำตอบเร็ว ปล่อยให้ความรู้สึกชัดขึ้นเอง"],
    },
    "cards": [
        ["คนรัก (The Lovers)", "ความรักที่ต้องเลือกด้วยใจ"], ["ดวงดาว (The Star)", "ความหวังและการเริ่มต้นใหม่"],
        ["ดวงอาทิตย์ (The Sun)", "ความสุขที่ชัดเจนและจริงใจ"], ["ดวงจันทร์ (The Moon)", "ความรู้สึกที่ยังซ่อนอยู่"],
        ["จักรพรรดินี (The Empress)", "ความอบอุ่นและการดูแล"], ["สองถ้วย (Two of Cups)", "ใจที่ตรงกัน"],
        ["อัศวินถ้วย (Knight of Cups)", "คนที่กำลังจะเข้ามาพร้อมความรู้สึกดี"], ["ความยุติธรรม (Justice)", "ความชัดเจนและความจริงใจ"],
        ["สตรีนักบวช (High Priestess)", "ความลับในใจที่ยังไม่พูด"], ["วงล้อแห่งโชคชะตา (Wheel of Fortune)", "จังหวะใหม่ของความสัมพันธ์"],
        ["ฤๅษี (The Hermit)", "ช่วงเวลาที่เขาต้องการคิดคนเดียว"], ["ดาวและถ้วย (Ace of Cups)", "ความรู้สึกใหม่ที่เพิ่งเริ่ม"],
    ],
}

def feel():
    data = json.dumps(FEEL, ensure_ascii=False)
    body = (f'<p class="nav"><a href="./">🔮 ดวงใจ</a> · <a href="./#t">ไพ่ยิปซี</a> · <a href="lucky-name">เช็กชื่อมงคล</a> · <a href="daily/">ดวงวันนี้</a></p>'
            + "<h1>💭 เขาคิดยังไงกับเรา</h1>"
            + '<p class="sub">ตั้งจิตนึกถึงคนที่อยู่ในใจ แล้วดูว่าตอนนี้เขารู้สึกยังไงกับคุณ</p>'
            + '<div class="box" id="form"><label for="me">ชื่อคุณ (ชื่อเล่นก็ได้)</label><input id="me" placeholder="เช่น มิว" autocomplete="off">'
              '<label for="him">ชื่อคนที่นึกถึง</label><input id="him" placeholder="เช่น ต้น" autocomplete="off">'
              '<label for="rel">เขาเป็นใครสำหรับคุณ</label><select id="rel"><option value="crush">คนที่แอบชอบ</option><option value="talking">คนคุย</option>'
              '<option value="partner">แฟน</option><option value="ex">แฟนเก่า</option><option value="friend">เพื่อน หรือคนรู้จัก</option></select>'
              '<button class="btn" id="go">ตั้งจิตแล้วกดดู</button></div>'
            + '<div class="box" id="wait" hidden style="text-align:center"><p style="font-size:2rem;margin:0">🔮</p><p id="wt" style="margin:0">กำลังเชื่อมความรู้สึก…</p></div>'
            + '<div id="res" hidden></div>'
            + '<div class="box"><h2 style="margin-top:0">ดูยังไงให้แม่น</h2><ul style="margin:0">'
              "<li>ก่อนกด ให้หลับตานึกถึงหน้าของเขาสักครู่ แล้วถามในใจว่า เขารู้สึกยังไงกับฉัน</li>"
              "<li>ชื่อเดิมในวันเดียวกันจะได้คำตอบเดิม ผลจะเปลี่ยนทุกวัน มาดูใหม่ได้พรุ่งนี้</li>"
              "<li>ใช้เป็นแนวทางให้กำลังใจ ความรู้สึกจริงของเขารู้ได้ดีที่สุดจากการคุยกัน</li></ul></div>"
            + '<div class="box"><h2 style="margin-top:0">ดูต่อ</h2><p style="margin:0"><a class="tag" href="./">เปิดไพ่ยิปซีเรื่องความรัก</a> '
              '<a class="tag" href="./">ดวงเนื้อคู่ตามวันเกิด</a> <a class="tag" href="daily/">ดวงความรักวันนี้</a> <a class="tag" href="lucky-name">เช็กชื่อมงคล</a></p></div>'
            + """<style>.pc{text-align:center;font-size:3rem;font-weight:700;color:var(--gold);line-height:1.1}
.lv{text-align:center;font-size:1.2rem;font-weight:700;margin:2px 0 10px}
.hb{height:12px;background:var(--line);border-radius:8px;overflow:hidden;margin:0 0 14px}.hb i{display:block;height:100%;background:linear-gradient(90deg,var(--acc),#e85d9b);width:0;transition:width 1s}
.rs h3{margin:14px 0 2px;color:var(--acc)}.rs p{margin:0}</style>"""
            + f"<script>const F={data};\n{SHARE_JS}\n" + r"""
const $=id=>document.getElementById(id);
function hash(s){let h=2166136261;for(const c of s){h^=c.codePointAt(0);h=Math.imul(h,16777619)}return h>>>0}
function rng(seed){let a=seed||1;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function today(){return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Bangkok'}).format(new Date())}
const RELN={crush:'คนที่แอบชอบ',talking:'คนคุย',partner:'แฟน',ex:'แฟนเก่า',friend:'เพื่อน'};
$('go').onclick=()=>{
 const me=$('me').value.trim(),him=$('him').value.trim(),rel=$('rel').value;
 const seed=(me||him)?hash([me,him,rel,today()].join('|')):Math.floor(Math.random()*4294967295);
 const r=rng(seed),pick=a=>a[Math.floor(r()*a.length)];
 const w=[3,4,4,3,2,1],tot=w.reduce((a,b)=>a+b);let x=r()*tot,li=0;while(x>=w[li]){x-=w[li];li++}
 const L=F.levels[li],pct=L[0]+Math.floor(r()*(L[1]-L[0]+1));
 const feel=pick(L[3]),un=pick(F.unsaid),sg=pick(F.signs),ad=pick(F.advice[rel]),cd=pick(F.cards);
 $('res').hidden=true;$('wait').hidden=false;
 const msgs=['กำลังเชื่อมความรู้สึก…','กำลังอ่านใจ'+(him?' '+him:'เขา')+'…','เปิดไพ่ความรู้สึก…'];let k=0;$('wt').textContent=msgs[0];
 const iv=setInterval(()=>{k++;if(k<msgs.length)$('wt').textContent=msgs[k]},550);
 setTimeout(()=>{clearInterval(iv);$('wait').hidden=true;
  const who=him||'เขา';
  const res=$('res');
  res.innerHTML=`<div class="box rs"><p style="text-align:center;margin:0;color:var(--mute)">ความรู้สึกที่${who}มีต่อ${me||'คุณ'}วันนี้</p>
  <div class="pc">${pct}%</div><div class="hb"><i id="hbi"></i></div><p class="lv">${L[2]}</p>
  <h3>💗 ${who}รู้สึกยังไง</h3><p>${feel}</p>
  <h3>🤫 สิ่งที่${who}ยังไม่กล้าพูด</h3><p>${un}</p>
  <h3>👀 สัญญาณที่อาจได้เห็นเร็ว ๆ นี้</h3><p>${sg}</p>
  <h3>🃏 ไพ่ประจำความรู้สึก</h3><p>${cd[0]} · ${cd[1]}</p>
  <h3>🌷 คำแนะนำสำหรับ${RELN[rel]}</h3><p>${ad}</p>
  <p style="margin-top:12px;color:var(--mute);font-size:.85rem;text-align:center">${(me||him)?'ผลนี้เป็นของวันนี้ พรุ่งนี้มาดูใหม่ได้':'ใส่ชื่อเพื่อให้ได้คำตอบเฉพาะของคุณสองคน'} · เพื่อความบันเทิง</p></div>`;
  res.hidden=false;requestAnimationFrame(()=>requestAnimationFrame(()=>$('hbi').style.width=pct+'%'));
  const txt=`${who}รู้สึกกับ${me||'ฉัน'} ${pct}% "${L[2]}" 💭\nลองดูของคุณที่ https://duangjai.site/feel`;
  shareBox(res.firstElementChild,txt,'https://duangjai.site/feel','แชร์ให้เพื่อนลองดูบ้าง');
  res.scrollIntoView({behavior:'smooth',block:'start'});
 },1700);
};
</script>""")
    title = "เขาคิดยังไงกับเรา ดูดวงความรู้สึก คนที่นึกถึงรู้สึกยังไงกับเรา ฟรี – ดวงใจ"
    desc = "ตั้งจิตนึกถึงคนที่อยู่ในใจ ใส่ชื่อแล้วดูว่าเขารู้สึกยังไงกับคุณ คิดถึงไหม แอบชอบหรือเปล่า สิ่งที่เขาไม่กล้าพูด พร้อมคำแนะนำ ดูฟรี ผลเปลี่ยนทุกวัน"
    return page("feel", title, desc, body, "", og_title="เขาคิดยังไงกับเรา 💭 ลองดูความรู้สึกของคนที่นึกถึง")

# ---------------- เขียนไฟล์ ----------------
(ROOT / "lucky-name.html").write_text(checker(), encoding="utf-8")
(ROOT / "feel.html").write_text(feel(), encoding="utf-8")
(OUT / "index.html").write_text(name_index(), encoding="utf-8")
counts = {}
for slug, dname, start in DAYS:
    (OUT / f"{slug}.html").write_text(day_page(slug, dname, start), encoding="utf-8")
    counts[slug] = (len(names_grid(BOYS, start)), len(names_grid(GIRLS, start)))

sm = ROOT / "sitemap.xml"
s = sm.read_text(encoding="utf-8")
urls = [f"{SITE}/lucky-name", f"{SITE}/feel", f"{SITE}/name/"] + [f"{SITE}/name/{d[0]}" for d in DAYS]
add = "".join(f"<url><loc>{u}</loc></url>\n" for u in urls if f"<loc>{u}</loc>" not in s)
if add:
    s = s.replace("</urlset>", add + "</urlset>")
    sm.write_text(s, encoding="utf-8")
print("names per day (boys, girls):", counts)
