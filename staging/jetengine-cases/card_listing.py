"""Blocks content for the JetEngine listing item 'Case Card (new design)' (id 11687 on staging6)
and the three nested term listings. Mirrors card() in cases_build.py."""
import json
TERM_LISTINGS = {'service-types': 11745, 'association_types': 11746, 'association_industry': 11747}
ROW = ('<div class="cx-row" style="display: flex; gap: 10px; align-items: baseline;"><span style="flex: none; width: 118px; '
       'font-weight: 700; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: #4B5563;">{label}</span>'
       '<div class="cx-terms" style="display: flex; flex-wrap: wrap; gap: 6px; min-width: 0;">')
URL = "[jet_engine_data dynamic_field_post_object='post_id' dynamic_field_filter='yes' filter_callbacks={filter_callback=get_permalink} _parse_attrs=filter_callbacks]"
TITLE = "[jet_engine_data]"
LOGO = "[jet_engine_data dynamic_field_source='meta' dynamic_field_post_meta_custom='case_logo']"
ALT = "[jet_engine_data dynamic_field_source='meta' dynamic_field_post_meta_custom='case_logo_alt']"
# Clean photo crop (page meta case_card_photo, meta box meta-2); the featured image is the old composite with baked-in title text
THUMB = "<img src=\"[jet_engine_data dynamic_field_source='meta' dynamic_field_post_meta_custom='case_card_photo']\" alt=\"\" loading=\"lazy\" style=\"width: 100%; height: 100%; object-fit: cover; object-position: center; display: block;\">"


def html(s):
    return '<!-- wp:html -->\n' + s + '\n<!-- /wp:html -->'


def terms_grid(tax):
    a = {"lisitng_id": str(TERM_LISTINGS[tax]), "columns": 1, "columns_tablet": 1, "columns_mobile": 1,
         "terms_object_ids": "%current_id%", "terms_orderby": "name", "terms_order": "ASC", "terms_hide_empty": False,
         "not_found_message": "", "className": "cx-terms-grid"}
    return '<!-- wp:jet-engine/listing-grid ' + json.dumps(a) + ' /-->'


def card_content():
    head = ('<div class="cx-dcard" style="background: #FFFFFF; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; '
            'box-shadow: 0 10px 24px rgba(4,31,51,0.08); height: 100%;">'
            f'<a href="{URL}" style="display: flex; height: 210px; overflow: hidden; background: #041F33; text-decoration: none;">'
            '<div style="flex: 0 0 46%; box-sizing: border-box; padding: 18px 16px 16px 18px; display: flex; flex-direction: column; gap: 10px;">'
            f'<img src="{LOGO}" alt="{ALT}" loading="lazy" style="max-width: 100%; max-height: 34px; width: auto; height: auto; display: block; align-self: flex-start;">'
            '<div style="flex: 1; display: flex; align-items: center;"><span style="font-family: \'PT Serif\', Georgia, serif; font-weight: 700; color: #FFFFFF; font-size: 15px; line-height: 1.2;">'
            f'{TITLE}</span></div></div>'
            f'<span class="cx-feat" aria-hidden="true" style="flex: 1 1 0; min-width: 0; height: 100%; display: block;">{THUMB}</span></a>'
            '<div style="padding: 20px 22px 22px; display: flex; flex-direction: column; gap: 10px; flex: 1;">')
    parts = []
    for i, (tax, label) in enumerate([('service-types', 'Services'), ('association_types', 'Member Type'), ('association_industry', 'Industry')]):
        parts.append(html((head if i == 0 else '</div></div>') + ROW.format(label=label)))
        parts.append(terms_grid(tax))
    tail = ('</div></div><span style="margin-top: auto; padding-top: 8px;">'
            f'<a href="{URL}" style="color: #127196; font-weight: 700; text-decoration: none;">Read the case<span style="position: absolute; left: -9999px;">: {TITLE}</span></a></span></div></div>')
    parts.append(html(tail))
    return '\n'.join(parts)


PILL = html('<span class="cx-pill" style="display: inline-block; background: #D6EAF4; border-radius: 999px; padding: 4px 11px; font-size: 13px; font-weight: 700; color: #041F33;">'
            '[jet_engine_data dynamic_field_source="meta" dynamic_field_post_meta_custom="card_label"]</span>')

if __name__ == '__main__':
    print(json.dumps({'card': card_content(), 'pill': PILL}))
