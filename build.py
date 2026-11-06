#!/usr/bin/env python3
"""잠팝 사이트 만들기.

사용법:  python3 build.py
- data/popups.json  : 팝업 정보 (매주 여기만 고치면 됨)
- photos/           : 팝업 사진 (파일 이름 = 슬러그-번호.jpg)
- dist/             : GitHub에 올릴 결과물이 여기 생김
"""
import datetime as dt
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
WEEK = "월화수목금토일"
ENTRY = {
    "free": ("entry-free", "자유 입장"),
    "onsite": ("entry-onsite", "현장 예약"),
    "pre": ("entry-pre", "사전 예약"),
}

data = json.load(open(os.path.join(ROOT, "data/popups.json"), encoding="utf8"))
SITE = data["site"]
POPS = sorted(data["popups"], key=lambda p: (p["end"], p["start"]))
STYLE_INDEX = open(os.path.join(ROOT, "tpl_index_style.html"), encoding="utf8").read()
STYLE_POPUP = open(os.path.join(ROOT, "tpl_popup_style.html"), encoding="utf8").read()
SCRIPT = open(os.path.join(ROOT, "tpl_script.html"), encoding="utf8").read()
EXTRA_CSS = open(os.path.join(ROOT, "extra.css"), encoding="utf8").read()
EXTRA_JS = open(os.path.join(ROOT, "extra.js"), encoding="utf8").read()

e = lambda s: html.escape(str(s), quote=True)
day = lambda s: dt.date.fromisoformat(s)


def md(s):  # 11.6
    d = day(s)
    return f"{d.month}.{d.day}"


def mdw(s):  # 11.6(금)
    d = day(s)
    return f"{d.month}.{d.day}({WEEK[d.weekday()]})"


def head(title, desc, canonical, style):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{SITE["gtm"]}');</script>
<!-- End Google Tag Manager -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
{style.replace('</style>', EXTRA_CSS + '</style>')}
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={SITE["gtm"]}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<div class="wrap">
"""


def top(home):
    return f"""<header class="site-top">
  <a class="site-name" href="{home}"><span class="line2-dot">2</span>잠팝</a>
  <span class="updated">{mdw(SITE["updated"])} 업데이트</span>
</header>
"""


FOOT = """<footer class="site-foot">모든 후기는 운영자가 직접 다녀와서 작성합니다. 메뉴·가격은 방문 당시 기준이라 현장과 다를 수 있어요.</footer>
</div>
"""


def tail():
    return FOOT + "<script>" + EXTRA_JS + "</script>\n" + SCRIPT + "</body>\n</html>\n"


def badge(p):
    cls, label = ENTRY[p["entry"]]
    return f'<span class="entry {cls}">{label}</span>'


def tags(p):
    return " ".join("#" + e(t) for t in p["tags"])


def card(p, prefix=""):
    photo = f"{prefix}images/{p['slug']}-1.jpg"
    thumb = (f'<img class="thumb" src="{photo}" alt="{e(p["name"])}" loading="lazy">'
             if p["photos"] else '<div class="thumb" aria-hidden="true">사진<br>준비 중</div>')
    return f"""<li data-place="{e(p['place'])}" data-tags="{e(','.join(p['tags']))}" data-start="{p['start']}" data-end="{p['end']}">
  <a class="card" href="{prefix}popup/{p['slug']}.html" data-track="card_click" data-popup="{p['slug']}" data-place-name="{e(p['place'])}">
    {thumb}
    <div class="card-body">
      <div class="card-top">{badge(p)}<span class="soon d-day" data-dday></span></div>
      <div class="card-name">{e(p['name'])}</div>
      <div class="card-meta">
        <span>{e(p['place'])} {e(p['floor'])}</span>
        <span class="walk"><span class="line2-dot">2</span>개찰구에서 도보 {p['walk']}분</span>
        <span class="d-day">~{md(p['end'])}</span>
      </div>
      <div class="tags">{tags(p)}</div>
    </div>
  </a>
</li>"""


def chips(key, values, label):
    out = [f'<span class="filter-label">{label}</span>',
           f'<button class="chip" type="button" data-filter="{key}" data-value="all" aria-pressed="true">전체</button>']
    for v in values:
        shown = ("#" + v) if key == "tag" else v
        out.append(f'<button class="chip" type="button" data-filter="{key}" data-value="{e(v)}" aria-pressed="false">{e(shown)}</button>')
    return "".join(out)


def build_index():
    places, tagset = [], []
    for p in POPS:
        if p["place"] not in places:
            places.append(p["place"])
        for t in p["tags"]:
            if t not in tagset:
                tagset.append(t)
    n = len(POPS)
    m = SITE["month"]
    title = f"{m}월 잠실 팝업 — 지금 진행 중 | 잠팝"
    desc = (f"{m}월 잠실 팝업스토어 {n}곳을 한눈에. {'·'.join(places)} 팝업의 입장 방식, 위치, 가격을 "
            "직접 방문 후기로 정리했어요.")
    body = f"""<main>
  <h1 class="board-title">{m}월 잠실 팝업</h1>
  <p class="board-sub">지금 진행 중인 잠실 일대 팝업 <span id="live-count">{n}</span>곳 · 직접 다녀온 후기</p>
  <div class="filters">
    <div class="filter-toggles">
      <button class="ftoggle" type="button" id="toggle-place" data-panel="panel-place" aria-expanded="false" aria-controls="panel-place">장소 <b data-current="place">전체</b><span class="caret" aria-hidden="true"></span></button>
      <button class="ftoggle" type="button" id="toggle-tag" data-panel="panel-tag" aria-expanded="false" aria-controls="panel-tag">태그 <b data-current="tag">전체</b><span class="caret" aria-hidden="true"></span></button>
    </div>
    <div class="filter-panels">
      <div class="filter-row" id="panel-place">{chips('place', places, '장소')}</div>
      <div class="filter-row" id="panel-tag">{chips('tag', tagset, '태그')}</div>
    </div>
  </div>
  <div class="legend"><span class="legend-item"><span class="entry entry-free">자유 입장</span><span>예약 없이 바로 입장 (줄이 있으면 서서 대기)</span></span><span class="legend-item"><span class="entry entry-onsite">현장 예약</span><span>현장에서 QR·키오스크로 대기 등록 후 입장</span></span><span class="legend-item"><span class="entry entry-pre">사전 예약</span><span>방문 전 예약 필수 (네이버예약·캐치테이블 등)</span></span></div>
  <ul class="board" id="board">
{chr(10).join(card(p) for p in POPS)}
  </ul>
  <p class="empty" id="empty" hidden>조건에 맞는 팝업이 없어요. 필터를 바꿔보세요.</p>
  <details class="ended" id="ended" hidden><summary>종료된 팝업 <span id="ended-count">0</span>곳</summary><ul class="board" id="ended-board"></ul></details>
</main>
"""
    page = head(title, desc, SITE["base"], STYLE_INDEX) + top("index.html") + body + tail()
    open(os.path.join(DIST, "index.html"), "w", encoding="utf8").write(page)


def build_popup(p):
    slug = p["slug"]
    loc = f"{p['place']} {p['floor']}"
    cls, label = ENTRY[p["entry"]]
    title = f"{p['name']} 후기 | 위치·가격 ({loc}) - 잠실 팝업"
    desc = (f"{p['name']} {label}, {loc}, 잠실역 개찰구에서 도보 {p['walk']}분. "
            f"{md(p['start'])}~{md(p['end'])} 운영. 직접 방문한 입장 방식·상품 가격 후기.")

    photos = "".join(
        f'<button class="photo" type="button" data-index="{i}" data-src="../images/{slug}-{i+1}.jpg" '
        f'data-caption="{e(c)}" aria-label="사진 크게 보기"><img src="../images/{slug}-{i+1}.jpg" '
        f'alt="{e(c)}" loading="lazy"></button>'
        for i, c in enumerate(p["photos"]))

    facts = [f'<div class="fact"><dt>입장 방식</dt><dd>{badge(p)} <small>{e(p["wait"])}</small>'
             f'<small>마지막 방문: {mdw(p["visited"])}</small></dd></div>',
             f'<div class="fact"><dt>위치</dt><dd>{e(loc)}<small><span class="walk"><span class="line2-dot">2</span>'
             f'잠실역 2호선 개찰구에서 도보 {p["walk"]}분'
             + (f' · {e(p["spot"])}' if p["spot"] else "") + '</span></small></dd></div>',
             f'<div class="fact"><dt>운영 기간</dt><dd>{mdw(p["start"])} ~ {mdw(p["end"])}</dd></div>']
    if p.get("hours"):
        facts.append(f'<div class="fact"><dt>운영 시간</dt><dd>{e(p["hours"])}</dd></div>')
    if p.get("adult"):
        facts.append('<div class="fact"><dt>연령</dt><dd>만 19세 이상만 입장·구매 가능</dd></div>')

    r = p.get("review")
    if r and (r.get("items") or r.get("summary")):
        items = "".join(
            f'<li><div class="ri-head"><b>{e(it["name"])}</b><span>{e(it["price"])}</span></div>'
            f'<p>{e(it["text"])}</p></li>' for it in r.get("items", []))
        review = (f'<ul class="review-items">{items}</ul>' if items else "") + "".join(
            f'<p>{e(s)}</p>' for s in r.get("summary", []))
    else:
        review = '<p class="pending">후기 준비 중이에요.</p>'

    menu_html = []
    for sec in p.get("menu", []):
        rows = []
        for it in sec["items"]:
            b = f' <span class="mini-badge">{e(it["badge"])}</span>' if it.get("badge") else ""
            if it.get("was"):
                price = f'<s>{e(it["was"])}</s> <b>{e(it["price"])}</b>'
            elif it.get("price"):
                price = e(it["price"])
            else:
                price = ""
            rows.append(f'<tr><td>{e(it["name"])}{b}</td><td>{price}</td></tr>')
        menu_html.append(f'<h3>{e(sec["title"])}</h3><table class="goods"><tbody>{"".join(rows)}</tbody></table>')
    notes = "".join(f'<p class="note">{e(n)}</p>' for n in p.get("notes", []))

    official = (f'<div class="actions"><a class="btn btn-primary" href="{e(p["official"])}" target="_blank" '
                f'rel="noopener" data-track="official_click" data-popup="{slug}">공식 계정 보러가기</a></div>'
                if p.get("official") else "")

    body = f"""<main data-end="{p['end']}">
  <a class="crumb" href="../index.html">← {SITE['month']}월 잠실 팝업 목록</a>
  <p class="ended-banner" id="ended-banner" hidden>종료된 팝업이에요. 기록용으로 남겨둔 페이지입니다.</p>
  <div class="detail-head">
    <div class="card-top">{badge(p)}<span class="tags">{tags(p)}</span></div>
    <h1>{e(p['name'])}</h1>
    <div class="card-meta"><span>{e(loc)}</span><span class="d-day">{md(p['start'])} ~ {md(p['end'])}</span></div>
  </div>

  <div class="photo-strip">{photos}</div>
  <div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="사진 크게 보기">
    <button class="lb-btn lb-close" type="button" data-lb="close" aria-label="닫기">×</button>
    <button class="lb-btn lb-prev" type="button" data-lb="prev" aria-label="이전 사진">‹</button>
    <figure class="lb-figure"><img class="lb-img" alt=""><span class="thumb lb-empty"></span><figcaption class="lb-caption"></figcaption></figure>
    <button class="lb-btn lb-next" type="button" data-lb="next" aria-label="다음 사진">›</button>
  </div>

  <dl class="facts">
    {chr(10).join(facts)}
  </dl>

  <section class="block">
    <h2>직접 가본 후기</h2>
    {review}
  </section>

  <section class="block menu">
    <h2>판매 메뉴·가격</h2>
    {''.join(menu_html)}
    {notes}
  </section>

  {official}
</main>
"""
    page = head(title, desc, f"{SITE['base']}popup/{slug}.html", STYLE_POPUP) + top("../index.html") + body + tail()
    open(os.path.join(DIST, "popup", f"{slug}.html"), "w", encoding="utf8").write(page)


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "popup"))
    shutil.copytree(os.path.join(ROOT, "photos"), os.path.join(DIST, "images"))
    build_index()
    for p in POPS:
        build_popup(p)
    urls = [SITE["base"]] + [f"{SITE['base']}popup/{p['slug']}.html" for p in POPS]
    sm = "".join(f"  <url><loc>{u}</loc><lastmod>{SITE['updated']}</lastmod></url>\n" for u in urls)
    open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + sm + "</urlset>\n")
    open(os.path.join(DIST, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE['base']}sitemap.xml\n")
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    print("완료:", len(POPS), "개 팝업 →", DIST)


main()
