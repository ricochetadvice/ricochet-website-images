"""Site-wide fixes for the new ricochetadvice.com design.

apply(html, page_id=None) runs every fix below and returns the new HTML.
  link_card_images(html)  images inside a one-destination card link to that destination
  add_nav_dropdowns(html) header dropdown menus plus the "Let's talk" header button
  meet_links(html)        on-site "Meet with us" links point to /lets-talk/

Pure stdlib so it also runs in Pyodide. Every transform is idempotent and
only inserts or rewrites the exact spans it targets; the rest of the HTML is
left byte for byte as it was.
"""
import re, html as _html

VOID = {'img', 'br', 'input', 'meta', 'link', 'hr', 'source', 'area', 'col', 'embed', 'param', 'track', 'wbr', 'base'}
RAW_TEXT = {'script', 'style', 'textarea', 'title'}
TAG_RE = re.compile(r'<!--.*?-->|<(/?)([a-zA-Z][\w:-]*)((?:[^>"\']|"[^"]*"|\'[^\']*\')*)>', re.S)
ATTR_RE = re.compile(r'([^\s=/>]+)(?:\s*=\s*("([^"]*)"|\'([^\']*)\'|([^\s>]+)))?')


class El:
    __slots__ = ('tag', 'attrs', 'start', 'open_end', 'close_start', 'end', 'parent', 'children')

    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag, self.attrs, self.start, self.open_end = tag, attrs, start, open_end
        self.close_start = self.end = open_end
        self.parent, self.children = parent, []

    def get(self, k, d=''):
        return self.attrs.get(k, d)

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()

    def ancestors(self):
        p = self.parent
        while p is not None and p.tag != '#root':
            yield p
            p = p.parent


def parse_attrs(s):
    out = {}
    for m in ATTR_RE.finditer(s):
        v = m.group(3) if m.group(3) is not None else (m.group(4) if m.group(4) is not None else (m.group(5) or ''))
        out[m.group(1).lower()] = _html.unescape(v)
    return out


def parse(h):
    root = El('#root', {}, 0, 0, None)
    cur = root
    pos = 0
    while True:
        m = TAG_RE.search(h, pos)
        if not m:
            break
        pos = m.end()
        if m.group(0).startswith('<!--'):
            continue
        closing, tag = m.group(1), m.group(2).lower()
        if closing:
            # pop to the matching open element (tolerant of stray closes)
            n = cur
            while n is not root and n.tag != tag:
                n = n.parent
            if n is root:
                continue
            while cur is not n:
                cur.close_start = cur.end = m.start()
                cur = cur.parent
            n.close_start, n.end = m.start(), m.end()
            cur = n.parent
            continue
        el = El(tag, parse_attrs(m.group(3)), m.start(), m.end(), cur)
        cur.children.append(el)
        if tag in VOID or m.group(3).rstrip().endswith('/'):
            el.close_start = el.end = m.end()
            continue
        if tag in RAW_TEXT:
            j = h.lower().find('</' + tag, m.end())
            j = len(h) if j < 0 else j
            k = h.find('>', j)
            el.close_start, el.end = j, (k + 1 if k >= 0 else len(h))
            pos = el.end
            continue
        cur = el
    while cur is not root:
        cur.close_start = cur.end = len(h)
        cur = cur.parent
    root.end = root.close_start = len(h)
    return root


def splice(h, edits):
    """edits: list of (start, end, text). Applied right to left, no overlaps."""
    for s, e, t in sorted(edits, key=lambda x: (x[0], x[1]), reverse=True):
        h = h[:s] + t + h[e:]
    return h


def style(el):
    return el.get('style').replace(' ', '').lower()


# ---------------------------------------------------------------- Fix 1
LINK_ATTRS = 'href="{href}" tabindex="-1" aria-hidden="true" style="display:block"'
CARD_HINTS = ('border-radius', 'border:', 'box-shadow', 'background:#fff', 'background:#ffffff', 'background:rgba(255,255,255')
SKIP_HREF = ('#', 'javascript:', 'mailto:', 'tel:')


def is_image(el):
    if el.tag == 'img':
        return True
    if el.tag in ('div', 'span', 'figure') and el.get('role') == 'img' and 'background-image' in style(el):
        return True
    return False


def card_hrefs(card, img):
    """distinct destinations inside the card, ignoring links that wrap the image."""
    hrefs = []
    for e in card.walk():
        if e.tag == 'a' and e.get('href'):
            if img.start >= e.start and img.end <= e.end:
                continue
            hrefs.append(e.get('href').strip())
        elif e.tag == 'button' and e is not img:
            hrefs.append('<button>')
        elif e.tag == 'form':
            hrefs.append('<form>')
    norm = []
    for x in hrefs:
        k = x.split('#')[0] if not x.startswith('#') else x
        if k not in norm:
            norm.append(k)
    return hrefs, norm


def _px(st, prop):
    m = re.search(r'(?:^|;)' + prop + r':(\d+(?:\.\d+)?)px', st)
    return float(m.group(1)) if m else None


def is_small(e):
    st = style(e)
    w, hgt = _px(st, 'width'), _px(st, 'height')
    return (w is not None and w <= 64) or (hgt is not None and hgt <= 64 and w is None)


def _meaningful(e):
    if not is_image(e):
        return False
    st = style(e)
    if 'position:absolute' in st or e.get('aria-hidden') == 'true' or is_small(e):
        return False
    return True


def has_form(card):
    for e in card.walk():
        if e.tag in ('form', 'script', 'iframe', 'select', 'input'):
            return True
        c = e.get('class')
        if 'form' in c or 'meetings-iframe' in c:
            return True
    return False


def find_card(img):
    """nearest ancestor that holds a link. A card-like box (li, article, bordered or
    rounded panel) may hold two images; a plain block must hold just this one.
    Never a hero (h1) and never above the section."""
    for a in img.ancestors():
        if a.tag in ('header', 'footer', 'nav', 'main', 'body', 'html', 'form'):
            return None
        kids = [e for e in a.walk() if e is not a]
        has_link = any(e.tag in ('a', 'button') and not (img.start >= e.start and img.end <= e.end) for e in kids)
        if not has_link:
            if a.tag == 'section':
                return None
            continue
        if any(e.tag == 'h1' for e in kids):
            return None
        imgs = [e for e in kids if _meaningful(e)]
        st = style(a)
        cardlike = a.tag in ('li', 'article') or any(k in st for k in CARD_HINTS)
        if has_form(a):
            return None
        if is_small(img) and not cardlike:
            return None
        if len(imgs) <= (2 if cardlike else 1):
            return a
        return None
    return None


def link_card_images(h, report=None):
    root = parse(h)
    edits, linked, skipped = [], 0, []
    done_cards = set()
    for img in root.walk():
        if not is_image(img):
            continue
        anc = list(img.ancestors())
        if any(a.tag in ('a', 'button', 'header', 'footer', 'nav', 'label') for a in anc):
            continue
        st = style(img)
        if 'position:absolute' in st or 'position:fixed' in st:
            continue
        if img.tag == 'img' and img.get('aria-hidden') == 'true' and img.get('alt', None) == '':
            pass  # decorative image inside a card can still be a click target; keep going
        # skip images whose wrapper is absolutely positioned decoration
        if img.parent is not None and img.parent.tag != '#root' and 'position:absolute' in style(img.parent) and img.parent.get('aria-hidden') == 'true':
            continue
        card = find_card(img)
        if card is None:
            continue
        hrefs, dest = card_hrefs(card, img)
        if not dest:
            continue
        label = _card_label(h, card)
        if len(dest) != 1 or dest[0].startswith(SKIP_HREF) or dest[0] in ('<button>', '<form>'):
            if len(dest) > 1:
                skipped.append({'card': label, 'hrefs': dest})
            continue
        href = next(x for x in hrefs if x.split('#')[0] == dest[0] or x == dest[0])
        # wrap the image, or the image's own frame div when it only holds the image
        target = img
        p = img.parent
        if p is not None and p is not card and p.tag == 'div' and len(p.children) == 1 and not _text_between(h, p, img):
            target = p
        open_tag = '<a ' + LINK_ATTRS.format(href=_html.escape(href, quote=True)) + '>'
        carry = _placement(target)
        if carry:
            open_tag = open_tag[:-2] + ';' + carry + '">'
        edits.append((target.start, target.start, open_tag))
        edits.append((target.end, target.end, '</a>'))
        linked += 1
        done_cards.add(card.start)
    if report is not None:
        report['cards_linked'] = report.get('cards_linked', 0) + linked
        report.setdefault('skipped_two_dest', []).extend(skipped)
    return splice(h, edits) if edits else h


PLACE_PROPS = ('flex', 'flex-grow', 'flex-shrink', 'flex-basis', 'align-self', 'justify-self', 'order',
               'grid-column', 'grid-row', 'grid-area', 'min-width', 'max-width')


def _placement(el):
    """flex/grid placement declarations of el, copied onto its new link wrapper."""
    out = []
    for decl in el.get('style').split(';'):
        if ':' not in decl:
            continue
        k, v = decl.split(':', 1)
        k = k.strip().lower()
        if k in PLACE_PROPS or k.startswith('margin'):
            out.append(f'{k}:{v.strip()}')
    st = style(el)
    if 'flex' in [d.split(':')[0] for d in out] or any(d.startswith('flex:') for d in out):
        pass
    w = re.search(r'(?:^|;)width:(\d+(?:\.\d+)?%)', st)
    if w:
        out.append('width:' + w.group(1))
    return ';'.join(out)


def _text_between(h, outer, inner):
    a = h[outer.open_end:inner.start]
    b = h[inner.end:outer.close_start]
    return re.sub(r'<[^>]+>|\s', '', a + b)


def _card_label(h, card):
    for e in card.walk():
        if e.tag in ('h2', 'h3', 'h4', 'strong', 'span', 'p'):
            t = re.sub(r'<[^>]+>', '', h[e.open_end:e.close_start]).strip()
            if 3 <= len(t) <= 90:
                return _html.unescape(re.sub(r'\s+', ' ', t))
    return h[card.start:card.start + 80]


# ---------------------------------------------------------------- Fix 2
MENUS = [
    ('Services', '/services/', [
        ('Member Research', '/services/member-research/'),
        ('Membership Modeling', '/services/membership-modeling/'),
        ('Brand and Campaign Studio', '/services/brand-and-campaign-studio/'),
        ('Tech and AI Roadmaps', '/services/tech-and-ai-roadmaps/'),
        ('Fractional Staffing and Training', '/services/fractional-staffing-and-training/'),
    ]),
    ('Academy', '/academy/', [
        ('All Access Pass', '/academy/all-access-pass/'),
        ('AI Accelerator', '/academy/association-ai-accelerator-certificate-course/'),
        ('Conference Architecture', '/academy/association-conference-architecture-certificate-course/'),
        ('Membership Growth', '/academy/association-membership-growth-certificate-course/'),
        ('Newsletter Success', '/academy/association-newsletter-success-certificate-course/'),
        ('SEO', '/academy/association-search-engine-optimization-certificate-course/'),
        ('Credentials', '/academy/credentials/'),
    ]),
    ('Mailchimp', '/mailchimp/', [
        ('Implementation', '/mailchimp/mailchimp-implementation/'),
        ('AMS Connector', '/mailchimp/mailchimp-ams-connector/'),
        ('Evolution Coaching', '/mailchimp/mailchimp-evolution-coaching/'),
    ]),
    ('HubSpot', '/hubspot/', [
        ('Implementation', '/hubspot/hubspot-implementation/'),
        ('AMS Connector', '/hubspot/hubspot-ams-connector/'),
        ('Evolution Coaching', '/hubspot/hubspot-evolution-coaching/'),
        ('Preferences Portal', '/hubspot/hubspot-preferences-portal/'),
    ]),
    ('Cases', '/cases/', [
        ('Member Research', '/service-types/member-research/'),
        ('Membership Modeling', '/service-types/membership-strategy/'),
        ('Brand and Campaign Studio', '/service-types/marketing-campaigns/'),
        ('Tech and AI Roadmaps', '/service-types/technology-roadmap/'),
        ('Fractional Staffing and Training', '/service-types/fractional-leadership-and-training/'),
        ('HubSpot', '/service-types/hubspot-automation/'),
        ('-', None),
        ('Individual membership associations', '/association-types/individual/'),
        ('Trade associations', '/association-types/trade/'),
    ]),
    ('About', '/about/', [
        ('Events', '/events/'),
        ("Let's Talk", '/lets-talk/'),
    ]),
]

LETS_TALK = '/lets-talk/'
SCHEDULE_RE = re.compile(r'^https?://(www\.)?schedulechris\.com/?$')
NO_LT_PAGES = {10313, 10477}  # Let's Talk and its thank-you: /lets-talk/ would loop there

NAV_CSS = '''<style id="rico-nav-css">
.rico-page>p:empty,.rico-page>br,.rico-page>p>br:only-child{display:none}
.rico-page>header,.rico-page>section,.rico-page>footer{margin-top:0;margin-bottom:0}
.rico-nav{display:flex;gap:28px;align-items:center;flex-wrap:wrap}
.rico-nav .rico-dd{position:relative;display:flex;align-items:center}
.rico-nav .rico-dd>a{color:#FFFFFF;font-weight:700;font-size:16px;text-decoration:none;display:inline-flex;align-items:center;min-height:44px}
.rico-nav .rico-dd-btn{display:inline-flex;align-items:center;justify-content:center;width:28px;min-height:44px;margin-left:2px;padding:0;background:transparent;border:0;color:#FFFFFF;cursor:pointer;border-radius:4px}
.rico-nav .rico-dd-btn svg{width:12px;height:12px;transition:transform .15s}
.rico-nav .rico-dd-btn[aria-expanded="true"] svg{transform:rotate(180deg)}
.rico-nav .rico-dd-panel{position:absolute;top:100%;left:-16px;z-index:50;min-width:260px;margin:0;padding:8px;list-style:none;background:#041F33;border:1px solid rgba(255,255,255,0.14);border-radius:8px;box-shadow:0 12px 28px rgba(4,31,51,0.35);opacity:0;visibility:hidden;transform:translateY(4px);transition:opacity .15s,transform .15s,visibility .15s}
.rico-nav .rico-dd-panel li{margin:0}
.rico-nav .rico-dd-panel .rico-dd-sep{height:1px;margin:6px 10px;background:rgba(255,255,255,0.18)}
.rico-nav .rico-dd-panel a{display:flex;align-items:center;min-height:44px;padding:10px 14px;border-radius:6px;color:#FFFFFF;font-family:'PT Sans',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif;font-weight:400;font-size:16px;line-height:1.3;text-decoration:none;white-space:nowrap}
.rico-nav .rico-dd-panel a:hover{background:rgba(255,255,255,0.10);opacity:1}
.rico-nav a:focus-visible,.rico-nav .rico-dd-btn:focus-visible{outline:3px solid #F0A500;outline-offset:2px}
.rico-nav .rico-dd:hover>.rico-dd-panel,.rico-nav .rico-dd:focus-within>.rico-dd-panel,.rico-nav .rico-dd.is-open>.rico-dd-panel{opacity:1;visibility:visible;transform:none}
.rico-nav .rico-dd.is-closed>.rico-dd-panel{opacity:0;visibility:hidden}
.rico-nav .rico-cta{display:inline-flex;align-items:center;justify-content:center;gap:0;min-height:48px;padding:0 35px;background:#D91A36;color:#FFFFFF;border-radius:4px;font-weight:700;font-size:17px;text-decoration:none;transition:background-color .15s,transform .15s,box-shadow .15s,gap .15s,padding .15s}
.rico-nav .rico-cta .rico-cta-arrow{display:inline-block;width:0;overflow:hidden;opacity:0;transform:translateX(-6px);transition:width .15s,opacity .15s,transform .15s}
.rico-nav .rico-cta:hover,.rico-nav .rico-cta:focus-visible{background:#B3142C;opacity:1;transform:translateY(-2px);box-shadow:0 6px 16px rgba(217,26,54,0.35);gap:8px;padding:0 24px}
.rico-nav .rico-cta:hover .rico-cta-arrow,.rico-nav .rico-cta:focus-visible .rico-cta-arrow{width:14px;opacity:1;transform:none}
@media (prefers-reduced-motion:reduce){.rico-nav .rico-dd-panel,.rico-nav .rico-dd-btn svg,.rico-nav .rico-cta,.rico-nav .rico-cta .rico-cta-arrow{transition:none}.rico-nav .rico-cta:hover,.rico-nav .rico-cta:focus-visible{transform:none;box-shadow:none;gap:0;padding:0 35px}.rico-nav .rico-cta:hover .rico-cta-arrow,.rico-nav .rico-cta:focus-visible .rico-cta-arrow{width:0;opacity:0}}
@media (max-width:767px){
.rico-nav{width:100%;flex-direction:column;align-items:stretch!important;gap:0!important}
.rico-nav .rico-dd{flex-wrap:wrap;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.12)}
.rico-nav .rico-dd>a{flex:1 1 auto}
.rico-nav .rico-dd-btn{width:44px}
.rico-nav .rico-dd-panel{position:static;flex:1 1 100%;min-width:0;display:none;opacity:1;visibility:visible;transform:none;box-shadow:none;border:0;padding:0 0 8px 12px;background:transparent}
.rico-nav .rico-dd:hover>.rico-dd-panel,.rico-nav .rico-dd:focus-within>.rico-dd-panel{display:none}
.rico-nav .rico-dd.is-open>.rico-dd-panel{display:block}
.rico-nav .rico-dd-panel a{white-space:normal}
.rico-nav .rico-cta{margin-top:14px;justify-content:center}
}
</style>'''

# no double ampersand anywhere: WordPress mangles it inside wp:html
NAV_JS = '''<script id="rico-nav-js">
(function(){
var nav=document.querySelector('.rico-nav');
if(!nav){return;}
var dds=nav.querySelectorAll('.rico-dd');
function setOpen(dd,open){
var b=dd.querySelector('.rico-dd-btn');
if(b){b.setAttribute('aria-expanded',open?'true':'false');}
if(open){dd.classList.add('is-open');dd.classList.remove('is-closed');}
else{dd.classList.remove('is-open');}
}
function closeAll(except){for(var i=0;i<dds.length;i++){if(dds[i]!==except){setOpen(dds[i],false);}}}
for(var i=0;i<dds.length;i++){(function(dd){
var b=dd.querySelector('.rico-dd-btn');
if(b){b.addEventListener('click',function(e){e.preventDefault();var open=b.getAttribute('aria-expanded')!=='true';closeAll(dd);setOpen(dd,open);if(!open){dd.classList.add('is-closed');}});}
dd.addEventListener('mouseleave',function(){dd.classList.remove('is-closed');});
dd.addEventListener('focusout',function(e){if(!dd.contains(e.relatedTarget)){setOpen(dd,false);dd.classList.remove('is-closed');}});
})(dds[i]);}
document.addEventListener('keydown',function(e){
if(e.key==='Escape'){
var a=document.activeElement;
for(var i=0;i<dds.length;i++){
if(dds[i].contains(a)){setOpen(dds[i],false);dds[i].classList.add('is-closed');var b=dds[i].querySelector('.rico-dd-btn');if(b){b.focus();}}
else{if(dds[i].classList.contains('is-open')){setOpen(dds[i],false);}}
}
}
});
document.addEventListener('click',function(e){if(!nav.contains(e.target)){closeAll(null);}});
})();
</script>'''

CHEVRON = '<svg viewBox="0 0 12 12" aria-hidden="true" focusable="false"><path d="M2 4.5l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<span class="rico-cta-arrow" aria-hidden="true">&rarr;</span>'


def nav_markup(cta_href, ident='rico-dd'):
    parts = []
    for i, (label, href, items) in enumerate(MENUS):
        pid = f'{ident}-{label.lower()}'
        lis = ''.join('<li class="rico-dd-sep" role="separator"></li>' if u is None else f'<li><a href="{_html.escape(u, quote=True)}">{_html.escape(t)}</a></li>' for t, u in items)
        parts.append(
            f'<div class="rico-dd"><a href="{href}">{label}</a>'
            f'<button type="button" class="rico-dd-btn" aria-expanded="false" aria-controls="{pid}" aria-label="{label} menu">{CHEVRON}</button>'
            f'<ul class="rico-dd-panel" id="{pid}">{lis}</ul></div>')
    parts.append(f'<a class="rico-cta" href="{_html.escape(cta_href, quote=True)}">Let&rsquo;s talk{ARROW}</a>')
    return '\n'.join(parts)


def _cta_href(page_id, current=None):
    if page_id in NO_LT_PAGES:
        if current and current.rstrip('/') not in ('/lets-talk', ''):
            return current
        return 'https://www.schedulechris.com'
    return LETS_TALK


def _refresh_nav(h, page_id):
    """page already converted: rebuild the menu, CSS and script from the current MENUS."""
    i = h.index('<nav class="rico-nav"')
    j = h.index('</nav>', i) + len('</nav>')
    cur = re.search(r'<a class="rico-cta" href="([^"]*)"', h[i:j])
    open_tag = h[i:h.index('>', i) + 1]
    h = h[:i] + open_tag + '\n' + nav_markup(_cta_href(page_id, cur.group(1) if cur else None)) + '\n</nav>' + h[j:]
    h = re.sub(r'<style id="rico-nav-css">.*?</style>', lambda m: NAV_CSS, h, count=1, flags=re.S)
    h = re.sub(r'<script id="rico-nav-js">.*?</script>', lambda m: NAV_JS, h, count=1, flags=re.S)
    return h


def add_nav_dropdowns(h, page_id=None, report=None):
    if '<nav class="rico-nav"' in h:
        out = _refresh_nav(h, page_id)
        if report is not None and out != h:
            report['nav'] = True
        return out
    root = parse(h)
    hdr = next((e for e in root.walk() if e.tag == 'header'), None)
    if hdr is None:
        return h
    nav = next((e for e in hdr.walk() if e.tag == 'nav' and e.get('aria-label') == 'Main'), None)
    if nav is None:
        return h
    links = [e for e in nav.children if e.tag == 'a']
    labels = [re.sub(r'<[^>]+>', '', h[e.open_end:e.close_start]).strip() for e in links]
    if labels[:6] != [m[0] for m in MENUS]:
        return h
    cta = links[6] if len(links) > 6 else None
    cta_href = _cta_href(page_id, cta.get('href') if cta is not None else None)
    open_tag = h[nav.start:nav.open_end].replace('<nav ', '<nav class="rico-nav" ', 1)
    out = h[:nav.start] + open_tag + '\n' + nav_markup(cta_href) + '\n</nav>' + h[nav.end:]
    # CSS right before the header, script right after it
    out = out[:hdr.start] + NAV_CSS + out[hdr.start:]
    j = out.index('</header>', hdr.start + len(NAV_CSS)) + len('</header>')
    out = out[:j] + NAV_JS + out[j:]
    if report is not None:
        report['nav'] = True
    return out


# ---------------------------------------------------------------- Fix 3
def meet_links(h, page_id=None, report=None):
    if page_id in NO_LT_PAGES:
        return h
    root = parse(h)
    edits = []
    for e in root.walk():
        if e.tag != 'a' or not SCHEDULE_RE.match(e.get('href').strip()):
            continue
        txt = re.sub(r'<[^>]+>', '', h[e.open_end:e.close_start]).strip()
        if txt != 'Meet with us':
            continue
        tag = h[e.start:e.open_end]
        new = re.sub(r'href="https?://(www\.)?schedulechris\.com/?"', 'href="' + LETS_TALK + '"', tag, count=1)
        if new != tag:
            edits.append((e.start, e.open_end, new))
    if report is not None:
        report['meet_links'] = report.get('meet_links', 0) + len(edits)
    return splice(h, edits) if edits else h


# ---------------------------------------------------------------- Fix 4
# Client logo tiles (200x104, Home marquee): equal visual weight. Each logo's trimmed
# content box is sized to the NSTA/NTMA average area (5230 px2), capped at 72% of
# tile width and 46% of tile height. Values: element width, height, translate x, y.
LOGO_SIZES = {
    'aao-hns-american-academy-of-otolaryngology-head-and-neck-surgery-logo.webp': (144, 34, 0, 0),
    'aapa-american-academy-of-physician-associates-logo.webp': (93, 48, 0, 0),
    'acep-american-college-of-emergency-physicians-logo.webp': (144, 27, 0, 0),
    'adlm-association-for-diagnostics-and-laboratory-medicine-logo.webp': (144, 26, 0, 0),
    'aenc-association-executives-of-north-carolina-logo.webp': (114, 46, 0, 0),
    'anitab-org-logo.webp': (138, 38, 0, 0),
    'ans-american-nuclear-society-logo.webp': (89, 48, 0, 0),
    'aota-american-occupational-therapy-association-logo.webp': (144, 28, 0, 1.7),
    'ara-american-retirement-association-logo.webp': (140, 38, 0, 0),
    'asco-american-society-of-clinical-oncology-logo.webp': (141, 38, 0, 0),
    'bscai-building-service-contractors-association-international-logo.webp': (145, 26, 0, 0),
    'cha-catholic-health-association-logo.webp': (114, 46, 0, 0),
    'cms-colorado-medical-society-logo.webp': (144, 33, 0, 0),
    'corenet-global-logo.webp': (144, 31, 0, 0),
    'crew-network-logo.webp': (126, 41, 0, 0),
    'cvma-colorado-veterinary-medical-association-logo.webp': (102, 48, 0, 0),
    'dcpa-logo.webp': (139, 38, 0, 0),
    'fei-financial-executives-international-logo.webp': (118, 44, 0, 0),
    'felinevma-feline-veterinary-medical-association-logo.webp': (144, 29, 0, 0),
    'ficpa-florida-institute-of-cpas-logo.webp': (115, 46, 0, 0),
    'finseca-logo.webp': (129, 41, 0, 0),
    'hardi-heating-air-conditioning-and-refrigeration-distributors-international-logo.webp': (132, 41, 0, 0),
    'hfa-home-furnishings-association-logo.webp': (143, 37, 0, 0),
    'iaee-international-association-of-exhibitions-and-events-logo.webp': (144, 24, 0, 0),
    'icf-international-coaching-federation-logo.webp': (145, 37, 0, 0),
    'iiaba-independent-insurance-agents-and-brokers-of-america-logo.webp': (144, 28, 0, 0),
    'isa-international-sign-association-logo.webp': (112, 47, 0, 0),
    'leadingage-logo.webp': (133, 40, 0, 0),
    'mipi-alliance-logo.webp': (144, 35, 0, 0),
    'nata-national-athletic-trainers-association-logo.webp': (116, 46, 0, 0),
    'ncacpa-north-carolina-association-of-cpas-logo.webp': (76, 48, 0, 0),
    'ncada-north-carolina-association-of-defense-attorneys-logo.webp': (144, 29, 0, 0),
    'ncan-national-college-attainment-network-logo.webp': (94, 48, 0, 0),
    'njcpa-new-jersey-society-of-cpas-logo.webp': (145, 27, 0, 0),
    'nsta-national-science-teaching-association-logo.webp': (190, 71, 0, -1.4),
    'ntma-national-tooling-and-machining-association-logo.webp': (144, 28, 0, 0),
    'payo-payroll-org-logo.webp': (100, 48, 0, 0),
    'rh-isac-retail-and-hospitality-isac-logo.webp': (144, 28, 0, 0),
    'rotary-international-logo.webp': (119, 44, 0, 0),
    'saba-san-antonio-bar-association-logo.webp': (144, 29, 0, 0),
    'sfn-society-for-neuroscience-logo.webp': (132, 40, 0, 0),
    'sifma-securities-industry-and-financial-markets-association-logo.webp': (100, 48, 0, 0),
    'smithbucklin-logo.webp': (144, 19, 0, 0),
    'vmae-veterinary-medical-association-executives-logo.webp': (111, 48, 0, 0),
    'wcet-wiche-cooperative-for-educational-technologies-logo.webp': (126, 42, 0, 0),
    'wscpa-washington-society-of-cpas-logo.webp': (145, 31, 0, 0),
}
OLD_TILE_IMG = 'style="width: 100%; height: 76px; object-fit: contain; display: block;"'
TILE_IMG_RE = re.compile(r'<img src="([^"]*?/([^/"]+\.webp))"([^>]*?)style="(?:width: 100%; height: 76px; object-fit: contain; display: block;|flex: none; width: \d+px; height: \d+px; display: block;(?: transform: translate\([^)]*\);)?)"')


def logo_style(fname):
    z = LOGO_SIZES.get(fname)
    if not z:
        return None
    w, hh, tx, ty = z
    tf = f' transform: translate({tx}px, {ty}px);' if (tx or ty) else ''
    return f'flex: none; width: {w}px; height: {hh}px; display: block;{tf}'


def standardize_logos(h, report=None):
    i = h.find('class="rico-marquee"')
    if i < 0:
        return h
    j = h.find('</section>', i)
    j = len(h) if j < 0 else j
    seg = h[i:j]
    n = [0]

    def rep(m):
        st = logo_style(m.group(2))
        if st is None:
            return m.group(0)
        new = f'<img src="{m.group(1)}"{m.group(3)}style="{st}"'
        if new != m.group(0):
            n[0] += 1
        return new
    seg2 = TILE_IMG_RE.sub(rep, seg)
    if report is not None:
        report['logos_resized'] = report.get('logos_resized', 0) + n[0]
    return h[:i] + seg2 + h[j:]


# ---------------------------------------------------------------- Fix 5
# Pages stored as plain HTML run through wpautop, which drops <p>/<br> around inline
# scripts, the header button and JSON-LD and opens white gaps between components.
# Wrapping the page in one core/html block turns wpautop off for it. The block
# mangles a double ampersand, so known filter code is rewritten first.
AMP_FIXES = [(
    "return(!s.value||c.dataset.s.split('|').indexOf(s.value)>-1)&&(!m.value||c.dataset.m===m.value)&&(!i.value||c.dataset.i===i.value);",
    "if(s.value){if(c.dataset.s.split('|').indexOf(s.value)<0){return false;}}if(m.value){if(c.dataset.m!==m.value){return false;}}if(i.value){if(c.dataset.i!==i.value){return false;}}return true;",
)]


def wrap_html_block(h, report=None):
    if h.lstrip().startswith('<!-- wp:'):
        return h
    for a, b in AMP_FIXES:
        h = h.replace(a, b)
    if '&' + '&' in h:
        if report is not None:
            report['wrap_skipped_amp'] = True
        return h
    if report is not None:
        report['wrapped'] = True
    return '<!-- wp:html -->\n' + h.strip('\n') + '\n<!-- /wp:html -->'


def apply(h, page_id=None, report=None):
    try:
        page_id = int(page_id) if page_id is not None else None
    except ValueError:
        page_id = None
    h = add_nav_dropdowns(h, page_id, report)
    h = meet_links(h, page_id, report)
    h = link_card_images(h, report)
    h = standardize_logos(h, report)
    h = wrap_html_block(h, report)
    return h
