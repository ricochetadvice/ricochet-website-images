"""Dynamic (JetEngine) case grids for the new-design Cases pages.

Replaces the static <ul class="cx-grid"> / <ul id="f-grid"> grids with a JetEngine Listing Grid block
(listing item 11687 'Case Card (new design)') and, on the landing, JetSmartFilters select filters.
Used by casesub_build.py / cases_build.py and by the staging patcher (patch_pages.js).
IDs are staging6 IDs; see README.md in this folder.
"""
import json, re

CARD_LISTING = 11687
QUERY_ALL = 11            # Query Builder: Cases (new design): all  (12 per page, load more)
# Query Builder ids per sub-landing term key (posts_per_page -1)
QUERY_BY_TERM = {
    'member-research': 12, 'membership-strategy': 13, 'marketing-campaigns': 14, 'technology-roadmap': 15,
    'fractional-leadership-and-training': 16, 'hubspot-automation': 17, 'individual': 18, 'trade': 19,
    'finance': 20, 'healthcare': 21, 'mfg-retail': 22, 'science-tech': 23, 'service': 24,
}
FILTERS = [(11894, 'Services'), (11895, 'Member Type'), (11896, 'Industry')]  # JetSmartFilters, manual options -> term ids
JSF_QUERY_ID = 'cases'

CSS = ('<style id="cx-dyn-css">'
       '.cx-dyn>.jet-listing-grid>.jet-listing-grid__items{display:flex!important;flex-wrap:wrap!important;justify-content:center;gap:22px;margin:0!important;padding:0!important;width:100%!important}'
       '.cx-dyn>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item{flex:0 0 calc((100% - 44px) / 3)!important;max-width:calc((100% - 44px) / 3)!important;width:auto!important;padding:0!important;margin:0!important;min-width:0;display:flex}'
       '.cx-dyn>.jet-listing-grid>.jet-listing-grid__items:has(>.jet-listing-grid__item:nth-child(4):last-child)>.jet-listing-grid__item{flex-basis:calc((100% - 22px) / 2)!important;max-width:calc((100% - 22px) / 2)!important}'
       '.cx-dyn.cx-landing>.jet-listing-grid>.jet-listing-grid__items{justify-content:flex-start}'
       '.cx-dyn.cx-landing>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item{flex-basis:calc((100% - 44px) / 3)!important;max-width:calc((100% - 44px) / 3)!important}'
       '.cx-dyn .cx-dcard{flex:1 1 auto;width:100%;height:auto!important}'
       '.cx-dyn .cx-feat img{width:100%!important;height:100%!important;max-width:none!important;object-fit:cover;display:block}'
       '.cx-dyn .cx-terms .jet-listing-grid--blocks,.cx-dyn .cx-terms .jet-listing-grid{margin:0;padding:0;min-width:0}'
       '.cx-dyn .cx-terms .jet-listing-grid__items{display:flex!important;flex-wrap:wrap!important;gap:6px;margin:0!important;padding:0!important;width:auto!important}'
       '.cx-dyn .cx-terms .jet-listing-grid__item{flex:none!important;width:auto!important;max-width:none!important;padding:0!important;margin:0!important}'
       '.cx-dyn .jet-listing-not-found{font-size:18px;color:#4B5563}'
       '.cx-filters .jet-select__control{appearance:auto;width:100%;background:#FFFFFF;border:1px solid #D1D5DB;border-radius:10px;padding:12px 14px;font-size:17px;color:#041F33;font-family:inherit;line-height:1.3;height:auto}'
       '.cx-filters .jet-smart-filters-select,.cx-filters .jet-select{width:100%}'
       '.cx-filters .jet-remove-all-filters__button{background:none!important;border:0!important;padding:0!important;color:#127196!important;font-weight:700;font-size:16px;font-family:inherit;cursor:pointer;text-decoration:none}'
       '@media (max-width:1023px){.cx-dyn>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item,.cx-dyn.cx-landing>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item,.cx-dyn>.jet-listing-grid>.jet-listing-grid__items:has(>.jet-listing-grid__item:nth-child(4):last-child)>.jet-listing-grid__item{flex-basis:calc((100% - 22px) / 2)!important;max-width:calc((100% - 22px) / 2)!important}}'
       '@media (max-width:767px){.cx-filters>div{flex:1 1 100%!important}.cx-dyn>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item,.cx-dyn.cx-landing>.jet-listing-grid>.jet-listing-grid__items>.jet-listing-grid__item,.cx-dyn>.jet-listing-grid>.jet-listing-grid__items:has(>.jet-listing-grid__item:nth-child(4):last-child)>.jet-listing-grid__item{flex-basis:100%!important;max-width:100%!important}}'
       '</style>')

LABEL = 'font-weight: 700; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #4B5563;'


def _block(name, attrs):
    return f'<!-- wp:{name} {json.dumps(attrs, separators=(",", ":"))} /-->'


def _break(inner):
    """Close the surrounding wp:html block, insert blocks, reopen it."""
    return '\n<!-- /wp:html -->\n' + inner + '\n<!-- wp:html -->\n'


def sub_grid(term_key):
    """Replacement for <ul class="cx-grid ...">...</ul> on a sub-landing page."""
    g = _block('jet-engine/listing-grid', {
        'lisitng_id': str(CARD_LISTING), 'columns': 3, 'columns_tablet': 2, 'columns_mobile': 1,
        'custom_query': True, 'custom_query_id': str(QUERY_BY_TERM[term_key]),
        'not_found_message': 'New case studies are on the way.', 'className': 'cx-dyn'})
    return CSS + _break(g)


def landing_grid():
    """Replacement for the landing filter row, count line, <ul id="f-grid"> and the Show more button."""
    parts = ['<div class="cx-filters" style="display: flex; flex-wrap: wrap; gap: 18px; align-items: flex-end;">']
    blocks = []
    for fid, label in FILTERS:
        blocks.append(f'<!-- wp:html -->\n<div style="flex: 1 1 220px; min-width: 0; display: flex; flex-direction: column; gap: 6px;"><span style="{LABEL}">{label}</span>\n<!-- /wp:html -->')
        blocks.append(_block('jet-smart-filters/select', {'filter_id': fid, 'content_provider': 'jet-engine', 'apply_type': 'ajax', 'query_id': JSF_QUERY_ID}))
        blocks.append('<!-- wp:html -->\n</div>\n<!-- /wp:html -->')
    blocks.append('<!-- wp:html -->\n<div style="flex: 0 0 auto; align-self: flex-end; padding-bottom: 12px;">\n<!-- /wp:html -->')
    blocks.append(_block('jet-smart-filters/remove-filters', {'content_provider': 'jet-engine', 'apply_type': 'ajax', 'query_id': JSF_QUERY_ID, 'remove_filters_text': 'Reset'}))
    blocks.append('<!-- wp:html -->\n</div></div>\n<!-- /wp:html -->')
    blocks.append(_block('jet-engine/listing-grid', {
        'lisitng_id': str(CARD_LISTING), 'columns': 3, 'columns_tablet': 2, 'columns_mobile': 1,
        'custom_query': True, 'custom_query_id': str(QUERY_ALL), '_element_id': JSF_QUERY_ID,
        'use_load_more': True, 'load_more_type': 'click', 'load_more_id': 'f-more',
        'not_found_message': 'No case studies match these filters. Try Reset.', 'className': 'cx-dyn cx-landing'}))
    tail = ('<div style="display: flex; justify-content: center;"><button id="f-more" type="button" style="background: #041F33; color: #FFFFFF; border: 0; border-radius: 999px; padding: 14px 26px; font-weight: 700; font-size: 16px; cursor: pointer; font-family: inherit;">Show more case studies</button></div>')
    return CSS + parts[0] + '\n<!-- /wp:html -->\n' + '\n'.join(blocks) + '\n<!-- wp:html -->\n' + tail


SUB_RE = re.compile(r'<ul class="cx-grid[^"]*"[^>]*>.*?</ul>', re.S)
LAND_RE = re.compile(r'<div style="display: flex; flex-wrap: wrap; gap: 18px; align-items: flex-end;">.*?Show more case studies</button></div>', re.S)
LAND_JS_RE = re.compile(r'<script>\(function\(\)\{var P=12,.*?</script>', re.S)


def to_dynamic_sub(content, term_key):
    out, n = SUB_RE.subn(lambda m: sub_grid(term_key), content, count=1)
    assert n == 1, 'static grid not found'
    return out


def to_dynamic_landing(content):
    out, n = LAND_RE.subn(lambda m: landing_grid(), content, count=1)
    assert n == 1, 'landing grid not found'
    out, n2 = LAND_JS_RE.subn('', out, count=1)
    assert n2 == 1, 'landing filter script not found'
    return out


if __name__ == '__main__':
    print(json.dumps({'css': CSS, 'sub': {k: sub_grid(k) for k in QUERY_BY_TERM}, 'landing': landing_grid()}))
