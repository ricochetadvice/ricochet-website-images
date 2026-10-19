import json,re,html,os
S='/tmp/claude-0/-home-claude/5ef27e7a-e2a6-5e53-a430-fc7f826a7365/scratchpad/'
src=open(S+'build/gen.py').read(); exec(src[:src.index('PAGES={')])  # body, fix, CSS, page helpers
import sys as _sys; _sys.path.insert(0,S+'build'); import sitefix  # header dropdowns, card image links, Let's talk links, logo sizes, wp:html wrap
P=S+'home-canvas/project/'
E=html.escape
copy=[]; [copy.extend(json.load(open(S+f'cases-copy/copy{i}.json'))) for i in (1,2,3)]
glance={r['slug']:r for r in json.load(open(S+'cases-glance/cases-at-a-glance.json'))}
ov=json.load(open(S+'cases-copy/overrides.json')) if os.path.exists(S+'cases-copy/overrides.json') else {}
B2F=json.load(open(S+'blob2file.json'))
a=open(P+'ALogos.dc.html').read(); L=json.loads(re.search(r'const LOGOS = (\[.*?\]);',a,re.S).group(1))
logo={}
for l in L:
    logo[l['href'].rstrip('/').split('/')[-1]]=(UP+B2F[l['src'].split('/')[-1]],l['name'])
logo['isa-explains-the-ai-future-with-seminar']=logo['isa-cleans-and-unifies-its-distributed-data']
logo['iaee-educates-members-with-ai-workshop']=logo['iaee-sets-its-digital-future']
SERV=['Member Research','Membership Modeling','Brand and Campaign Studio','Tech and AI Roadmaps','Fractional Staffing and Training','HubSpot','Mailchimp']
PILL='<span style="background: #D6EAF4; border-radius: 999px; padding: 4px 11px; font-size: 13px; font-weight: 700; color: #041F33;">{}</span>'
SERIF="font-family: 'PT Serif', Georgia, serif; font-weight: 700; color: #041F33;"
def rec(c):
    g=glance[c['slug']]; o=ov.get(c['slug'],{})
    r=dict(c); r.update(o.get('copy',{}))
    r['g']=dict(g); r['g'].update(o.get('glance',{}))
    return r
cases=[rec(c) for c in copy]
order=[s for s in glance]  # newest first already
cases.sort(key=lambda c: order.index(c['slug']))
def url(c): return f"https://ricochetadvice.com/cases/{c['slug']}/"
def tags(c,small=False):
    g=c['g']; rows=[('Services',g['services']),('Member Type',[g['member_type']]),('Industry',[g['industry']])]
    return ''.join(f'<div style="display: flex; gap: 10px; align-items: baseline;"><span style="flex: none; width: 118px; font-weight: 700; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #4B5563;">{k}</span><div style="display: flex; flex-wrap: wrap; gap: 6px;">{"".join(PILL.format(E(x)) for x in v if x)}</div></div>' for k,v in rows)
def card(c,extra=''):
    lg,nm=logo[c['slug']]
    return (f'<li{extra} style="background: #FFFFFF; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 10px 24px rgba(4,31,51,0.08);">'
     f'<a href="{url(c)}" style="display: flex; height: 210px; overflow: hidden; background: #041F33; text-decoration: none;"><div style="flex: 0 0 46%; box-sizing: border-box; padding: 18px 16px 16px 18px; display: flex; flex-direction: column; gap: 10px;">'
     f'<img src="{lg}" alt="{E(nm)} logo" loading="lazy" style="max-width: 100%; max-height: 34px; width: auto; height: auto; display: block; align-self: flex-start;">'
     f'<div style="flex: 1; display: flex; align-items: center;"><span style="font-family: \'PT Serif\', Georgia, serif; font-weight: 700; color: #FFFFFF; font-size: 15px; line-height: 1.2;">{E(c["title"])}</span></div></div>'
     f'<img src="{{{{FEAT:{c["slug"]}}}}}" alt="" aria-hidden="true" loading="lazy" style="flex: 1 1 0; min-width: 0; height: 100%; object-fit: cover; display: block;"></a>'
     f'<div style="padding: 20px 22px 22px; display: flex; flex-direction: column; gap: 10px; flex: 1;">{tags(c)}'
     f'<span style="margin-top: auto; padding-top: 8px;"><a href="{url(c)}" style="color: #127196; font-weight: 700; text-decoration: none;">Read the case<span style="position: absolute; left: -9999px;">: {E(c["title"])}</span></a></span></div></li>')
def glance_rows(c):
    g=c['g']; rows=[('Association',E(g['association_display'] if g.get('association_display') else g['association']))]
    m=g.get('members') or {}
    if m.get('display'): rows.append((m['display_label'],E(m['display'])))
    rows.append(('Services',''.join(PILL.format(E(x)) for x in g['services'])))
    rows.append(('Member Type',PILL.format(E(g['member_type']))))
    rows.append(('Industry',PILL.format(E(g['industry']))))
    for e in g.get('extra',[]): rows.append((e['label'],E(e['value'])))
    return ''.join(f'<div style="display: flex; flex-direction: column; gap: 2px; padding: 12px 0; border-top: 1px solid #D1D5DB;"><span style="font-weight: 700; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: #4B5563;">{E(k)}</span><span style="font-size: 17px; color: #041F33; display: flex; flex-wrap: wrap; gap: 6px;">{v}</span></div>' for k,v in rows)
def related(c):
    p=c['preheader'].replace(' case study','')
    same=[x for x in cases if x['slug']!=c['slug'] and p in x['g']['services']]
    other=[x for x in cases if x['slug']!=c['slug'] and x not in same]
    return (same+other)[:3]
def case_page(c):
    hero=(f'<section style="background: #D6EAF4; font-family: \'PT Sans\', -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif; color: #333333;"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; min-height: 640px; display: flex; flex-wrap: wrap; gap: 56px; align-items: center;"><div style="flex: 0 1 560px; min-width: 0; display: flex; flex-direction: column; gap: 22px;">'
      f'<div style="font-weight: 700; font-size: 14px; line-height: 1; letter-spacing: 0.14em; text-transform: uppercase; color: #041F33;">{E(c["preheader"])}</div>'
      '<div style="width: 96px; height: 5px; background: linear-gradient(90deg, #D91A36 0%, #D91A36 10%, #E8763A 46%, #F0A500 86%, #F0A500 100%);"></div>'
      f'<h1 style="margin: 0; {SERIF} font-size: 56px; line-height: 1.08; letter-spacing: -0.02em;">{E(c["title"])}</h1>'
      f'<p style="margin: 0; font-size: 22px; line-height: 1.55; color: #1F2D3A;">{E(c["summary"])}</p></div>'
      f'<div style="flex: 1 1 480px; min-width: 0;"><div style="border-radius: 18px; overflow: hidden; box-shadow: 0 24px 48px rgba(4,31,51,0.18);"><img src="{{{{FEAT:{c["slug"]}}}}}" alt="{E(c["short_name"])} case study feature image." style="width: 100%; height: auto; display: block;"></div></div></div></section>')
    secs=''.join(f'<div style="display: flex; flex-direction: column; gap: 12px;"><h2 style="margin: 0; {SERIF} font-size: 36px; line-height: 1.2; letter-spacing: -0.01em;">{E(s["heading"])}</h2><p style="margin: 0; font-size: 19px; line-height: 1.65;">{E(s["body"])}</p></div>' for s in c['sections'])
    story=(f'<section style="background: #FFFFFF; font-family: \'PT Sans\', -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif; color: #333333;"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; display: flex; flex-wrap: wrap; gap: 64px; align-items: flex-start;">'
      f'<div style="flex: 1.6 1 560px; min-width: 0; display: flex; flex-direction: column; gap: 44px;">{secs}</div>'
      f'<aside style="flex: 1 1 320px; min-width: 0; background: #F0EBE3; border-radius: 16px; padding: 26px 28px; display: flex; flex-direction: column; gap: 4px;"><span style="{SERIF} font-size: 22px; margin-bottom: 8px;">At a glance</span>{glance_rows(c)}'
      f'<p style="margin: 16px 0 0; font-size: 17px; line-height: 1.5;">{E(c["cta_hook"])} <a href="https://www.schedulechris.com" style="color: #127196; font-weight: 700; text-decoration: none;">Meet with us</a></p></aside></div></section>')
    rel=(f'<section style="background: #F0EBE3; font-family: \'PT Sans\', -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif; color: #333333;"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 40px;"><div style="display: flex; flex-direction: column; gap: 16px; max-width: 860px;"><div style="font-weight: 700; font-size: 14px; line-height: 1; letter-spacing: 0.14em; text-transform: uppercase; color: #041F33;">More cases</div><h2 style="margin: 0; {SERIF} font-size: 44px; line-height: 1.16; letter-spacing: -0.02em;">Explore more cases like this one</h2></div>'
      f'<ul style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px;">{"".join(card(x) for x in related(c))}</ul>'
      '<p style="margin: 0; font-size: 18px;"><a href="https://ricochetadvice.com/cases/" style="color: #127196; font-weight: 700; text-decoration: none;">See all case studies</a></p></div></section>')
    ld={"@context":"https://schema.org","@type":"Article","headline":c['title'],"description":c['summary'],"author":{"@type":"Organization","name":"Ricochet"},"publisher":{"@type":"Organization","name":"Ricochet"},"about":{"@type":"Organization","name":c['g'].get('association_display') or c['g']['association']}}
    out=CSS+f'<script type="application/ld+json">{json.dumps(ld)}</script><div class="rico-page" style="background:#FFFFFF;">'+'\n'.join([body('AHeader'),hero,story,rel,body('ACta'),body('AFooter')])+'</div>'
    return fix(out)
def landing():
    hero=body('CSHero')
    sv=body('CSServices')
    sv=sv.replace('Brand and Campaign Studios<','Brand and Campaign Studio<')
    # Mailchimp card dropped (no Mailchimp cases); six cards on an even grid (6 / 3 / 2 columns)
    sv=re.sub(r'<li style="flex: 1 1 0; min-width: 0; display: flex;"><a href="#"(?:(?!</li>).)*?>Mailchimp</h3>.*?</li>','',sv,flags=re.S)
    SVG='<style>@media (max-width:1023px){.cs-svc{grid-template-columns:repeat(3,minmax(0,1fr))!important}}@media (max-width:767px){.cs-svc{grid-template-columns:repeat(2,minmax(0,1fr))!important}}</style><ul class="cs-svc" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 20px;">'
    sv=re.sub(r'<ul (?:class="cs-svc" )?style="list-style: none; margin: 0; padding: 0; display: (?:flex|grid);[^"]*">',lambda m:SVG,sv,count=1)
    assert 'Mailchimp</h3>' not in sv and sv.count('See the cases')==6
    names=['Member Research','Membership Modeling','Brand and Campaign Studio','Tech and AI Roadmaps','Fractional Staffing and Training','HubSpot']
    hrefs=iter(names)
    SUB={'Member Research':'/service-types/member-research/','Membership Modeling':'/service-types/membership-strategy/','Brand and Campaign Studio':'/service-types/marketing-campaigns/','Tech and AI Roadmaps':'/service-types/technology-roadmap/','Fractional Staffing and Training':'/service-types/fractional-leadership-and-training/','HubSpot':'/service-types/hubspot-automation/'}  # sub-landing pages (casesub_build.py)
    def _h(n): return 'https://ricochetadvice.com'+SUB[n] if n in SUB else f'https://ricochetadvice.com/cases/?service={n.replace(" ","+")}#find'
    sv=re.sub(r'<a href="#"',lambda m:f'<a href="{_h(next(hrefs))}"',sv)
    mts=sorted({c['g']['member_type'] for c in cases}); inds=sorted({c['g']['industry'] for c in cases})
    def sel(id,label,opts): return (f'<div style="flex: 1 1 220px; min-width: 0; display: flex; flex-direction: column; gap: 6px;"><label for="{id}" style="font-weight: 700; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #4B5563;">{label}</label>'
        f'<select id="{id}" style="appearance: auto; background: #FFFFFF; border: 1px solid #D1D5DB; border-radius: 10px; padding: 12px 14px; font-size: 17px; color: #041F33; font-family: inherit;"><option value="">All</option>{"".join(f"<option>{E(o)}</option>" for o in opts)}</select></div>')
    items=''.join(card(c,f' class="rico-case" data-s="{E("|".join(c["g"]["services"]))}" data-m="{E(c["g"]["member_type"])}" data-i="{E(c["g"]["industry"])}"') for c in cases)
    grid=(f'<section id="find" style="background: #F0EBE3; font-family: \'PT Sans\', -apple-system, \'Segoe UI\', Helvetica, Arial, sans-serif; color: #333333;"><div style="max-width: 1280px; margin: 0 auto; padding: 96px 48px; box-sizing: border-box; display: flex; flex-direction: column; gap: 40px;"><div style="display: flex; flex-direction: column; gap: 16px; max-width: 860px;"><div style="font-weight: 700; font-size: 14px; line-height: 1; letter-spacing: 0.14em; text-transform: uppercase; color: #041F33;">Find a case</div><h2 style="margin: 0; {SERIF} font-size: 44px; line-height: 1.16; letter-spacing: -0.02em;">Which case studies match my association?</h2><p style="margin: 0; font-size: 20px; line-height: 1.55;">Filter by service, member type and industry.</p></div>'
      f'<div style="display: flex; flex-wrap: wrap; gap: 18px; align-items: flex-end;">{sel("f-s","Services",SERV)}{sel("f-m","Member Type",mts)}{sel("f-i","Industry",inds)}<div style="flex: 0 0 auto; align-self: flex-end; padding-bottom: 12px;"><a href="#find" id="f-reset" style="color: #127196; font-weight: 700; text-decoration: none;">Reset</a></div></div>'
      f'<p id="f-count" aria-live="polite" style="margin: 0; font-size: 17px; color: #4B5563;"></p>'
      f'<ul id="f-grid" style="list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 22px;">{items}</ul>'
      '<div style="display: flex; justify-content: center;"><button id="f-more" type="button" style="background: #041F33; color: #FFFFFF; border: 0; border-radius: 999px; padding: 14px 26px; font-weight: 700; font-size: 16px; cursor: pointer; font-family: inherit;">Show more case studies</button></div></div></section>')
    js='''<script>(function(){var P=12,shown=P,s=document.getElementById('f-s'),m=document.getElementById('f-m'),i=document.getElementById('f-i'),cards=[].slice.call(document.querySelectorAll('.rico-case')),more=document.getElementById('f-more'),cnt=document.getElementById('f-count');
function run(){var v=cards.filter(function(c){if(s.value){if(c.dataset.s.split('|').indexOf(s.value)<0){return false;}}if(m.value){if(c.dataset.m!==m.value){return false;}}if(i.value){if(c.dataset.i!==i.value){return false;}}return true;});cards.forEach(function(c){c.hidden=true;});v.forEach(function(c,k){c.hidden=k>=shown;});more.hidden=v.length<=shown;cnt.textContent=v.length+(v.length===1?' case study':' case studies');}
[s,m,i].forEach(function(el){el.addEventListener('change',function(){shown=P;run();});});
more.addEventListener('click',function(){shown+=P;run();});
document.getElementById('f-reset').addEventListener('click',function(e){e.preventDefault();s.value=m.value=i.value='';shown=P;run();});
var q=new URLSearchParams(location.search).get('service');if(q){for(var k=0;k<s.options.length;k++){if(s.options[k].text===q){s.value=q;}}}run();})();</script>'''
    css2='<style>.rico-case[hidden]{display:none!important}@media (max-width:1023px){#f-grid{grid-template-columns:1fr 1fr!important}}@media (max-width:767px){#f-grid{grid-template-columns:1fr!important}}</style>'
    out=CSS+css2+'<div class="rico-page" style="background:#FFFFFF;">'+'\n'.join([body('AHeader'),hero,sv,grid,body('ACta'),body('AFooter')])+'</div>'+js
    return fix(out)
os.makedirs(S+'build/cases',exist_ok=True)
for c in cases: open(S+f'build/cases/{c["slug"]}.html','w').write(sitefix.apply(case_page(c)))
sys_path_je='/home/claude/ricochet-website-images/staging/jetengine-cases'
_sys.path.insert(0,sys_path_je); import dyn_blocks  # JetEngine Listing Grid + JetSmartFilters replace the static grid and its filter script
open(S+'build/cases/_landing.html','w').write(dyn_blocks.to_dynamic_landing(sitefix.apply(landing())))
json.dump([{k:c[k] for k in ('slug','title')} for c in cases],open(S+'build/cases/_index.json','w'))
print(len(cases),'cases built')
