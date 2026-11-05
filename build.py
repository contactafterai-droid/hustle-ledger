#!/usr/bin/env python3
"""Build the Hustle Ledger site from data/*.json into dist/.

Scheduled runs only edit files in data/. This script turns them into:
  dist/index.html        the site (static, readable without JavaScript)
  dist/api/v1/*.json     the public read-only API
  dist/feed.xml          RSS feed of news (for RSS-to-email newsletters)
  dist/sitemap.xml, dist/robots.txt
No third-party packages required.
"""
import json, shutil, sys
from datetime import date, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA, DIST = ROOT / "data", ROOT / "dist"


def load(name):
    return json.loads((DATA / f"{name}.json").read_text())


def fmt(d):
    dt = date.fromisoformat(d)
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"


def check(site, facts, news):
    """Fail the build on data that would publish something wrong."""
    errors = []
    for f in facts["facts"]:
        if not f.get("source", "").startswith("https://"):
            errors.append(f"fact without https source: {f['item']}")
    for n in news["items"]:
        for k in ("date", "title", "summary", "source", "source_name"):
            if not n.get(k):
                errors.append(f"news item missing {k}: {n.get('title')}")
        date.fromisoformat(n["date"])
        if len(n["summary"]) > 320:
            errors.append(f"summary too long (keep it our own short words): {n['title']}")
    if errors:
        sys.exit("BUILD FAILED\n" + "\n".join(errors))


CSS = """
:root{--paper:#e9f0ed;--card:#f6f9f8;--ink:#11302a;--soft:#4d6862;--line:#c5d3ce;
--marker:#f4c21b;--note:#1f5c50;--warn:#9a3d12;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--paper:#0d1c19;--card:#132724;--ink:#e3eeea;
--soft:#97b0a9;--line:#2a4540;--marker:#e7b416;--note:#7cc7b4;--warn:#f0a070;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 "Public Sans",system-ui,sans-serif;
font-variant-numeric:tabular-nums}
a{color:var(--note);text-underline-offset:3px}
a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid var(--marker);outline-offset:2px}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
header.top{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:20px 0;flex-wrap:wrap}
.brand{font:700 22px/1 "Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.02em;color:var(--ink);text-decoration:none}
nav a{margin-left:18px;color:var(--soft);text-decoration:none;font-size:15px}
nav a:hover{color:var(--ink)}
.hero{padding:40px 0 48px;display:grid;grid-template-columns:1.1fr .9fr;gap:40px;align-items:end}
h1{font:800 clamp(44px,7vw,84px)/.95 "Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.035em;margin:0 0 20px}
.hero p{max-width:34ch;color:var(--soft);margin:0}
.count{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.count .row{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:10px 0;border-bottom:1px dashed var(--line)}
.count .row .mono{white-space:nowrap}
.count .row:last-child{border-bottom:0}
.count .big{font:800 56px/1 "Bricolage Grotesque",system-ui,sans-serif;
background:linear-gradient(transparent 58%,var(--marker) 58%,var(--marker) 92%,transparent 92%);padding:0 4px}
section{padding:44px 0;border-top:1px solid var(--line)}
h2{font:700 30px/1.1 "Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.02em;margin:0 0 8px}
.lede{color:var(--soft);margin:0 0 24px;max-width:62ch}
table{width:100%;border-collapse:collapse;font-size:16px}
th,td{text-align:left;padding:11px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-weight:600;color:var(--soft);font-size:14px}
.st{white-space:nowrap;font-size:14px;font-weight:600}
.st.confirmed{color:var(--note)}.st.na{color:var(--warn)}
.news{list-style:none;padding:0;margin:0;display:grid;gap:22px}
.news time{color:var(--soft);font-size:14px}
.news h3{font:700 20px/1.25 "Bricolage Grotesque",system-ui,sans-serif;margin:2px 0 6px}
.news p{margin:0 0 4px;max-width:68ch}
.news .src{font-size:14px}
.board{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px}
.board .empty{border:2px dashed var(--line);border-radius:10px;padding:22px;margin-top:16px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:28px}
ul.rules{padding-left:20px;margin:8px 0 0}
code,.mono{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:14px}
.api li{margin:6px 0}
form.sub{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
form.sub input{flex:1 1 240px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);font:inherit}
.btn{padding:12px 18px;border-radius:10px;border:0;background:var(--ink);color:var(--paper);font:600 16px "Public Sans",sans-serif;cursor:pointer;text-decoration:none;display:inline-block}
.btn[disabled]{opacity:.5;cursor:not-allowed}
footer{padding:36px 0 60px;color:var(--soft);font-size:14px;border-top:1px solid var(--line)}
.count .big{white-space:nowrap;color:#11302a;background:var(--marker);border-radius:6px;padding:2px 8px}
@media (max-width:760px){.hero,.two{grid-template-columns:1fr}nav a{margin:0 14px 0 0}
.count .big{font-size:40px}.count .row{flex-wrap:wrap}
th:nth-child(3),td:nth-child(3){display:none}}
"""


def render(site, facts, news, money, servers):
    rel = date.fromisoformat(facts["release_date"])
    days = (rel - date.today()).days
    count_label = f"{days} days" if days > 1 else ("Tomorrow" if days == 1 else "Out now")

    fact_rows = "".join(
        f"<tr><td>{escape(f['item'])}</td>"
        f"<td class='st {'confirmed' if f['status']=='confirmed' else 'na'}'>{escape(f['status'].capitalize())}</td>"
        f"<td>{escape(f['detail'])} <a href='{escape(f['source'])}' rel='nofollow noopener'>source</a></td></tr>"
        for f in facts["facts"])

    upcoming = "".join(
        f"<div class='row'><span>{escape(u['event'])}</span><span class='mono'>{fmt(u['date'])}</span></div>"
        for u in facts["upcoming"] if date.fromisoformat(u["date"]) >= date.today())

    items = sorted(news["items"], key=lambda n: n["date"], reverse=True)
    news_html = "".join(
        f"<li><time datetime='{n['date']}'>{fmt(n['date'])}</time><h3>{escape(n['title'])}</h3>"
        f"<p>{escape(n['summary'])}</p><a class='src' href='{escape(n['source'])}' rel='nofollow noopener'>"
        f"Reported by {escape(n['source_name'])}</a></li>" for n in items)

    known = "".join(
        f"<li><strong>{escape(k['system'])}:</strong> {escape(k['detail'])} "
        f"<a href='{escape(k['source'])}' rel='nofollow noopener'>source</a></li>" for k in money["known_systems"])
    if money["methods"]:
        rows = "".join(
            f"<tr><td>{i+1}</td><td>{escape(m['name'])}</td><td class='mono'>${m['per_hour']:,}</td>"
            f"<td>{escape(m.get('notes',''))}</td></tr>"
            for i, m in enumerate(sorted(money["methods"], key=lambda m: -m["per_hour"])))
        board = (f"<table><thead><tr><th>Rank</th><th>Method</th><th>In-game $ per hour</th><th>Notes</th></tr></thead>"
                 f"<tbody>{rows}</tbody></table>")
    else:
        board = (f"<div class='empty'><strong>Rankings go live after launch.</strong> {escape(money['note'])}"
                 f"<p style='margin:12px 0 0'>Systems confirmed so far:</p><ul class='rules'>{known}</ul></div>")

    if servers["servers"]:
        srv = "".join(
            f"<tr><td>{escape(s['name'])}{' (featured)' if s.get('featured') else ''}</td>"
            f"<td>{escape(s['game'])}</td><td>{escape(s['style'])}</td>"
            f"<td><a href='{escape(s['url'])}' rel='nofollow noopener'>Visit</a></td></tr>"
            for s in sorted(servers["servers"], key=lambda s: not s.get("featured")))
        srv = f"<table><thead><tr><th>Server</th><th>Game</th><th>Style</th><th></th></tr></thead><tbody>{srv}</tbody></table>"
    else:
        srv = "<div class='empty'><strong>Accepting the first listings.</strong> GTA V roleplay servers now, GTA 6 servers the day they exist.</div>"
    rules = "".join(f"<li>{escape(r)}</li>" for r in servers["listing_rules"])
    list_cta = (f"<a class='btn' href='{escape(site['featured_listing_url'])}'>Get a featured listing</a>"
                if site["featured_listing_url"] else
                f"<a class='btn' href='{escape(site['repo_url'])}/issues/new?template=server-listing.yml'>Submit your server</a>")

    if site["newsletter_form_action"]:
        sub = (f"<form class='sub' method='post' action='{escape(site['newsletter_form_action'])}'>"
               f"<label class='mono' for='em' style='flex-basis:100%'>Email address</label>"
               f"<input id='em' name='email' type='email' required autocomplete='email' placeholder='you@example.com'>"
               f"<button class='btn' type='submit'>Subscribe</button></form>")
    else:
        sub = ("<form class='sub' onsubmit='return false'><input type='email' disabled placeholder='Sign-up opens before launch'>"
               "<button class='btn' disabled>Subscribe</button></form>")

    base = site["base_url"].rstrip("/")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(site['name'])}: GTA 6 money methods, news and RP servers</title>
<meta name="description" content="Every confirmed GTA 6 fact with its source, money methods ranked by real hourly earnings after launch, and a roleplay server directory.">
<link rel="canonical" href="{base}/">
<link rel="alternate" type="application/rss+xml" title="{escape(site['name'])} news" href="{base}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=JetBrains+Mono&family=Public+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>
<div class="wrap">
<header class="top"><a class="brand" href="#">{escape(site['name'])}</a>
<nav><a href="#facts">Facts</a><a href="#money">Money</a><a href="#news">News</a><a href="#servers">Servers</a><a href="#api">API</a></nav></header>
<div class="hero"><div><h1>{escape(site['tagline'])}</h1>
<p>Confirmed facts with sources, money methods ranked by what they pay per real hour, and roleplay servers worth joining.</p></div>
<div class="count" aria-label="Countdown to launch"><div class="row"><span>GTA 6 launch</span><span class="big">{count_label}</span></div>{upcoming}</div></div>

<section id="facts"><h2>What's confirmed</h2><p class="lede">Checked against sources on {fmt(facts['verified_on'])}. Anything unconfirmed is marked so.</p>
<table><thead><tr><th>Item</th><th>Status</th><th>Detail</th></tr></thead><tbody>{fact_rows}</tbody></table></section>

<section id="money"><h2>Money board</h2><p class="lede">The fastest legitimate ways to get rich in story mode, ranked by in-game dollars per real hour.</p>
<div class="board">{board}</div></section>

<section id="news"><h2>News</h2><p class="lede">What changed, in plain words, with a link to who reported it.</p><ul class="news">{news_html}</ul></section>

<section id="servers" class="two"><div><h2>Roleplay servers</h2><p class="lede">A directory of servers that follow the platform rules, so they won't vanish overnight.</p>{srv}</div>
<div class="board"><strong>List your server</strong><p style="margin:6px 0 0">Listings are free. To be listed:</p><ul class="rules">{rules}</ul><p style="margin:16px 0 0">{list_cta}</p></div></section>

<section id="newsletter"><h2>The Ledger, weekly</h2><p class="lede">The best money method this week and what changed, in a two-minute email.</p>{sub}</section>

<section id="api"><h2>Free API</h2><p class="lede">The same data as this page, as JSON. Free to use with a link back.</p>
<ul class="api"><li><code>{base}/api/v1/facts.json</code></li><li><code>{base}/api/v1/news.json</code></li>
<li><code>{base}/api/v1/money-methods.json</code></li><li><code>{base}/api/v1/servers.json</code></li></ul></section>
</div>
<footer><div class="wrap">{escape(site['name'])} is a fan site. It is not affiliated with, approved, sponsored or endorsed by Rockstar Games or Take-Two Interactive. Game names are trademarks of their owners. <a href="{escape(site['repo_url'])}/issues/new">Contact us</a></div></footer>
</body></html>"""


def rss(site, news):
    base = site["base_url"].rstrip("/")
    items = sorted(news["items"], key=lambda n: n["date"], reverse=True)[:30]
    def rfc(d):
        return datetime.fromisoformat(d + "T12:00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
    body = "".join(
        f"<item><title>{escape(n['title'])}</title><link>{escape(n['source'])}</link>"
        f"<guid isPermaLink='false'>{n['date']}-{escape(n['title'])}</guid><pubDate>{rfc(n['date'])}</pubDate>"
        f"<description>{escape(n['summary'])} (Reported by {escape(n['source_name'])})</description></item>" for n in items)
    return (f"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel><title>{escape(site['name'])}</title>"
            f"<link>{base}/</link><description>{escape(site['tagline'])}</description>{body}</channel></rss>")


def main():
    site, facts, news = load("site"), load("facts"), load("news")
    money, servers = load("money-methods"), load("servers")
    check(site, facts, news)
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "api/v1").mkdir(parents=True)
    (DIST / "index.html").write_text(render(site, facts, news, money, servers))
    for name, obj in [("facts", facts), ("news", news), ("money-methods", money), ("servers", servers)]:
        (DIST / f"api/v1/{name}.json").write_text(json.dumps(obj, indent=2))
    (DIST / "feed.xml").write_text(rss(site, news))
    base = site["base_url"].rstrip("/")
    (DIST / "sitemap.xml").write_text(
        f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"
        f"<url><loc>{base}/</loc><lastmod>{date.today().isoformat()}</lastmod></url></urlset>")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    (DIST / ".nojekyll").write_text("")
    print("built", sorted(str(p.relative_to(DIST)) for p in DIST.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
