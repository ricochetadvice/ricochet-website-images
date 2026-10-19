"""Cases sub-landing pages (one per service term and member-type term).

Builds:
  build/casesub/<key>.html          WordPress content per term ({{FEAT:slug}} resolved at push time)
  casesub/project/CX*.dc.html       canvas section files + assembled Member Research example
"""
import json, re, os, sys, html
S = '/tmp/claude-0/-home-claude/5ef27e7a-e2a6-5e53-a430-fc7f826a7365/scratchpad/'
src = open(S + 'build/cases_build.py').read()
# reuse every helper from cases_build (records, card(), CSS, body(), fix()) without writing its files
exec(src[:src.index("os.makedirs(S+'build/cases'")])
sys.path.insert(0, S + 'build')
try:
    import sitefix
except ImportError:
    sitefix = None
# dynamic JetEngine grid (listing 11687 + Query Builder per term); see repo staging/jetengine-cases/README.md
sys.path.insert(0, '/home/claude/ricochet-website-images/staging/jetengine-cases')
import dyn_blocks

PROD = 'https://ricochetadvice.com'
# legacy taxonomy term -> new-design tag; path = the live term archive path, kept as the page path
TERMS = [
    dict(key='member-research', tax='service-types', slug='member-research', name='Member Research', kind='s',
         h1='What results has Ricochet delivered in member research?',
         intro='These associations asked their members directly, through member surveys and focus groups before changing course. Each study ended in a roadmap or growth strategy the staff could act on.'),
    dict(key='membership-strategy', tax='service-types', slug='membership-strategy', name='Membership Modeling', kind='s',
         h1='What results has Ricochet delivered in membership modeling?',
         intro='These associations redesigned membership tiers and dues with Ricochet, often after a merger or a long membership decline. AnitaB.org launched its first membership program 102 days after kickoff, and AAPA hit its revenue goals with a tiered model.'),
    dict(key='marketing-campaigns', tax='service-types', slug='marketing-campaigns', name='Brand and Campaign Studio', kind='s',
         h1='What results has Ricochet delivered in brand and campaign work?',
         intro='Recruitment and renewal campaigns for associations that needed members to see their value. CoreNet Global beat its recruitment goal with paid media, and AAO-HNS exceeded its revenue goals through its first major dues increase in years.'),
    dict(key='technology-roadmap', tax='service-types', slug='technology-roadmap', name='Tech and AI Roadmaps', kind='s',
         h1='What results has Ricochet delivered in technology roadmaps?',
         intro='Multi-year roadmaps and system selections for associations planning their next platforms. ACEP got a five-year roadmap that phases in new systems to limit disruption.'),
    dict(key='fractional-leadership-and-training', tax='service-types', slug='fractional-leadership-and-training', name='Fractional Staffing and Training', kind='s',
         h1='What results has Ricochet delivered through fractional staffing and training?',
         intro='Fractional marketers and CMOs stepped in when associations lost staff, and Ricochet workshops trained members and executives on growth and AI. At MIPI Alliance, a fractional marketer doubled the assigned workload.'),
    dict(key='hubspot-automation', tax='service-types', slug='hubspot-automation', name='HubSpot', kind='s',
         h1='What results has Ricochet delivered with HubSpot?',
         intro='HubSpot implementations for associations moving off older email systems, with Ricochet training staff to run the platform on their own. NATA completed its move in sixteen weeks.'),
    # term slug stays 'individual' (live taxonomy data); the page URL is /association-types/professional/ (301 from /individual/ at launch)
    dict(key='individual', tax='association-types', slug='professional', name='Individual', kind='m', label='Professional associations', chip='Professional Association',
         h1='How has Ricochet helped professional associations?',
         intro='Case studies from professional associations whose members join as individuals, from state CPA societies to national medical associations.'),
    dict(key='trade', tax='association-types', slug='trade', name='Trade', kind='m', label='Trade associations', chip='Trade Association',
         h1='How has Ricochet helped trade associations?',
         intro='Case studies from associations whose members are companies and institutions, from the sign industry to higher education technology.'),
    dict(key='finance', tax='association-industry', slug='finance', name='Finance', kind='i', label='Finance',
         h1='How has Ricochet helped finance associations?',
         intro='Case studies from CPA societies and financial services associations. WSCPA and FICPA both moved from Adestra to HubSpot Marketing Hub with Ricochet.'),
    dict(key='healthcare', tax='association-industry', slug='healthcare', name='Healthcare', kind='i', label='Healthcare',
         h1='How has Ricochet helped healthcare associations?',
         intro='Case studies from medical societies and veterinary associations. NATA moved to HubSpot in sixteen weeks, and AAPA hit its revenue goals with a tiered membership model.'),
    dict(key='mfg-retail', tax='association-industry', slug='mfg-retail', name='Mfg/Retail', kind='i', label='Manufacturing and Retail',
         h1='How has Ricochet helped manufacturing and retail associations?',
         intro='Case studies from manufacturing and retail associations. The International Sign Association had Ricochet review nearly 300,000 scattered records before its new AMS went live.'),
    dict(key='science-tech', tax='association-industry', slug='science-tech', name='Science/Tech', kind='i', label='Science and Technology',
         h1='How has Ricochet helped science and technology associations?',
         intro='Case studies from science and technology associations. AnitaB.org launched its first membership program 102 days after kickoff.'),
    dict(key='service', tax='association-industry', slug='service', name='Service', kind='i', label='Service',
         h1='How has Ricochet helped service industry associations?',
         intro='Case studies from associations in professional services and education. CoreNet Global beat its recruitment goal with paid media.'),
]
for t in TERMS:
    t['path'] = f"/{t['tax']}/{t['slug']}/"
    t.setdefault('label', t['name'])
    t['cases'] = [c for c in cases if (t['name'] in c['g']['services'] if t['kind'] == 's' else c['g']['member_type' if t['kind'] == 'm' else 'industry'] == t['name'])]

FONT = "font-family: 'PT Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; color: #333333;"
EYE = 'font-weight: 700; font-size: 14px; line-height: 1; letter-spacing: 0.14em; text-transform: uppercase; color: #041F33;'
BAR = '<div style="width: 96px; height: 5px; background: linear-gradient(90deg, #D91A36 0%, #D91A36 10%, #E8763A 46%, #F0A500 86%, #F0A500 100%);"></div>'
CHIP = 'display: inline-flex; align-items: center; min-height: 44px; padding: 10px 18px; border-radius: 999px; background: #F0EBE3; color: #041F33; font-weight: 700; font-size: 16px; line-height: 1.2; text-decoration: none;'
LABEL = 'font-weight: 700; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #4B5563;'


def hero(t):
    return (f'<section style="background: #D6EAF4; {FONT}"><div style="max-width: 1280px; margin: 0 auto; padding: 80px 48px 72px; box-sizing: border-box;">'
            f'<div style="display: flex; flex-direction: column; gap: 20px; max-width: 900px;">'
            f'<div style="{EYE}">Case studies</div>{BAR}'
            f'<h1 style="margin: 0; {SERIF} font-size: 56px; line-height: 1.08; letter-spacing: -0.02em;">{E(t["h1"])}</h1>'
            f'<p style="margin: 0; font-size: 21px; line-height: 1.55; color: #1F2D3A;">{E(t["intro"])}</p>'
            f'<p style="margin: 0; font-size: 18px;"><a href="{PROD}/cases/" style="color: #127196; font-weight: 700; text-decoration: none;">See all case studies</a></p>'
            '</div></div></section>')


def grid(t, cardfn):
    items = ''.join(cardfn(c) for c in t['cases'])
    return (f'<section style="background: #F0EBE3; {FONT}"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 40px;">'
            f'<h2 style="margin: 0; {SERIF} font-size: 36px; line-height: 1.2; letter-spacing: -0.01em;">{E(t["label"])} case studies</h2>'
            f'<ul class="cx-grid{" cx-2" if len(t["cases"]) == 4 else ""}" style="list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; justify-content: center; gap: 22px;">{items}</ul></div></section>')


def terms_row(t):
    def group(kind, label):
        lis = ''.join(f'<li><a href="{PROD}{x["path"]}" style="{CHIP}">{E(x["name"] if kind == "s" else x.get("chip", x["label"]))}</a></li>'
                      for x in TERMS if x['kind'] == kind and x['key'] != t['key'])
        return (f'<div style="display: flex; flex-direction: column; gap: 12px;"><span style="{LABEL}">{label}</span>'
                f'<ul style="list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 12px;">{lis}</ul></div>')
    return (f'<section style="background: #FFFFFF; {FONT}"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 32px;">'
            f'<div style="display: flex; flex-direction: column; gap: 16px; max-width: 860px;"><div style="{EYE}">Keep exploring</div>'
            f'<h2 style="margin: 0; {SERIF} font-size: 44px; line-height: 1.16; letter-spacing: -0.02em;">Which other case studies should I see?</h2></div>'
            f'{group("s", "By service")}{group("m", "By member type")}{group("i", "By industry")}'
            f'<p style="margin: 0; font-size: 18px;"><a href="{PROD}/cases/" style="color: #127196; font-weight: 700; text-decoration: none;">See all case studies</a></p></div></section>')


GRID_CSS = '.cx-grid>li{flex:0 0 calc((100% - 44px) / 3);max-width:calc((100% - 44px) / 3);min-width:0}.cx-grid.cx-2>li{flex-basis:calc((100% - 22px) / 2);max-width:calc((100% - 22px) / 2)}@media (max-width:1023px){.cx-grid>li,.cx-grid.cx-2>li{flex-basis:calc((100% - 22px) / 2);max-width:calc((100% - 22px) / 2)}}@media (max-width:767px){.cx-grid>li,.cx-grid.cx-2>li{flex-basis:100%;max-width:100%}}'  # 3 columns, 2 for four-case pages; lone last cards centre (no orphans at the edge)
CSS3 = '<style id="cx-grid-css">' + GRID_CSS + '</style>'


def ld(t):
    return json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": f'{t["label"]} case studies',
                       "description": t['intro'], "url": PROD + t['path'],
                       "isPartOf": {"@type": "WebPage", "name": "Case studies", "url": PROD + "/cases/"},
                       "mainEntity": {"@type": "ItemList", "numberOfItems": len(t['cases']), "itemListElement": [
                           {"@type": "ListItem", "position": i + 1, "name": c['title'], "url": url(c)} for i, c in enumerate(t['cases'])]}})


def wp_page(t):
    out = CSS + CSS3 + '<div class="rico-page" style="background:#FFFFFF;">' + '\n'.join(
        [body('AHeader'), hero(t), grid(t, card), terms_row(t), body('ACta'), body('AFooter')]) + '</div>'
    out = fix(out)
    out = f'<script type="application/ld+json">{ld(t)}</script>' + out
    rep = {}
    if sitefix:
        out = sitefix.apply(out, None, rep)
    else:
        out = '<!-- wp:html -->\n' + out + '\n<!-- /wp:html -->'
    # swap the static card grid for the JetEngine Listing Grid block (cards then come from the case pages' terms)
    out = dyn_blocks.to_dynamic_sub(out, t['key'])
    return out, rep


# ---------------- canvas
LOGOBLOB = {}
for l in L:
    LOGOBLOB[l['href'].rstrip('/').split('/')[-1]] = l['src']
LOGOBLOB['isa-explains-the-ai-future-with-seminar'] = LOGOBLOB['isa-cleans-and-unifies-its-distributed-data']
LOGOBLOB['iaee-educates-members-with-ai-workshop'] = LOGOBLOB['iaee-sets-its-digital-future']
FEATBLOB = {
    'ncans-strategic-pivot-to-a-sustainable-membership-model': '/_blob/7bbd879f20999482b133035076923f14',
    'ncada-transforms-a-pivotal-turning-point-into-a-growth-opportunity': '/_blob/9d4451ba518876a9b445682b4311d43b',
    'rh-isac-understands-their-members': '/_blob/1b263e1a3dc616264b9362543aa37c6e',
    'iiaba-explores-its-member-resources': '/_blob/8b7ac4e1c58f2ca7b4e99c80e5cd0f1a',
    'crew-charts-a-digital-future': '/_blob/f34013ca79d76d91d154d69378252fda',
    'iaee-sets-its-digital-future': '/_blob/2c634181c9ef04cf3c279193543891bd',
    'aafp-digital-transformation': '/_blob/87f45bc04fe27b58044eee18fe78b08e',
}


def canvas_card(c):
    h = card(c)
    nm = logo[c['slug']][0]
    h = h.replace(nm, LOGOBLOB[c['slug']]).replace('{{FEAT:%s}}' % c['slug'], FEATBLOB[c['slug']])
    return h.replace(' loading="lazy"', '')


def dc(title, inner, w, h, extra_style=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&amp;family=PT+Serif:wght@700&amp;display=swap">
<style>body{{margin:0}}{extra_style}</style>
</helmet>
{inner}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{ renderVals() {{ return {{}}; }} }}
</script>
</body>
</html>
'''


if __name__ == '__main__':
    os.makedirs(S + 'build/casesub', exist_ok=True)
    idx = []
    for t in TERMS:
        h, rep = wp_page(t)
        assert '&' + '&' not in h
        open(S + f'build/casesub/{t["key"]}.html', 'w').write(h)
        idx.append({k: t[k] for k in ('key', 'tax', 'slug', 'name', 'label', 'path', 'h1')} | {'cases': [c['slug'] for c in t['cases']], 'fix': rep})
        print(t['key'], len(t['cases']), rep)
    json.dump(idx, open(S + 'build/casesub/_index.json', 'w'), indent=1)
    # canvas
    t = TERMS[0]
    CP = S + 'casesub/project/'
    gcss = '.cx-grid img{max-width:100%}' + GRID_CSS
    open(CP + 'CXHero.dc.html', 'w').write(dc('Cases sub-landing hero', hero(t), 1440, 560))
    open(CP + 'CXGrid.dc.html', 'w').write(dc('Cases sub-landing grid', grid(t, canvas_card), 1440, 1640, gcss))
    open(CP + 'CXTerms.dc.html', 'w').write(dc('Cases sub-landing other terms', terms_row(t), 1440, 700))
    asm = ('<div style="font-family: \'PT Sans\', -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif; color: #333333; background: #FFFFFF;">\n'
           '<dc-import name="AHeader" hint-size="100%,100px"></dc-import>\n<dc-import name="CXHero" hint-size="100%,560px"></dc-import>\n'
           '<dc-import name="CXGrid" hint-size="100%,1640px"></dc-import>\n<dc-import name="CXTerms" hint-size="100%,700px"></dc-import>\n'
           '<dc-import name="ACta" hint-size="100%,440px"></dc-import>\n<dc-import name="AFooter" hint-size="100%,110px"></dc-import>\n</div>')
    open(CP + 'CasesMemberResearch.dc.html', 'w').write(dc('Member Research cases', asm, 1440, 3550).replace('<style>body{margin:0}</style>', '<style>body{margin:0}</style>', 1))
    print('canvas files written')
