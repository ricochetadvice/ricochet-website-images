# Dynamic case grids (JetEngine) for the new-design Cases pages

Staging6 build, 2026-10-18. All page edits are on drafts. Nothing was published or deleted.

## Architecture

- **Source of truth is the case page itself.** The 48 new case pages (children of 9951 "Cases (new design)") now carry the three existing taxonomies, so a page is the only record a new case needs. The `cases` CPT is no longer read by the new design.
- **Taxonomies** `service-types` (JetEngine tax 1), `association_types` (2), `association_industry` (3) now attach to `cases` and `page`. Term slugs and names are unchanged (live data).
- **Display labels** live in term meta `card_label` (meta box "Case card label", meta-3): Membership Strategy shows as Membership Modeling, Individual as Professional associations, Trade as Trade associations, and so on.
- **Page meta** (meta box "Case card (new design)", meta-2, pages): `case_logo` (media, URL) and `case_logo_alt`. Feature image is the WordPress featured image. Card order is `menu_order` ascending (10, 20, ... 480; a new page left at 0 shows first, newest first).
- **Listing items** (Blocks view): 11687 "Case Card (new design)" (source Pages) with three nested term listings 11745 (services), 11746 (member type), 11747 (industry). Card markup mirrors `card()` in `cases_build.py`. Content: `card-listing-content.json`, generator `card_listing.py`.
- **Query Builder**: 11 = landing (12 per page, load more); 12 to 24 = one per sub-landing term (see `dyn_blocks.QUERY_BY_TERM`). All filter `post_type=page`, `post_parent=9951`, ordered by menu_order. **They include drafts until launch** (`launch-flip-status.js`).
- **Filters** (JetSmartFilters, AJAX, provider jet-engine, query id `cases`): 11894 Services, 11895 Member type, 11896 Industry. Manual options mapped to term ids with query var `_tax_query::<taxonomy>`, so labels match the cards. The live production filters 1421/2199/2200 are untouched. Remove-filters block shows "Reset" when a filter is active.
- **Pages**: in 9951 and the 13 sub-landings only the static grid changed (landing: also the filter row, count line and the old filter script). `dyn_blocks.py` holds the exact replacement and the shared CSS (`style#cx-dyn-css`).

## Adding a case later

Create a child page of Cases with the case content, tick its Service Types, Association Types and Association Industry terms, set the featured image, fill Case logo and alt. It appears on the landing (with filtering) and on every matching sub-landing. A brand-new service term also needs an option added to filter 11894 and a `card_label`.

## Build scripts

`builders/casesub_build.py` and `builders/cases_build.py` (copies of the scratchpad builders) now emit the dynamic grid via `dyn_blocks.py`. Individual is relabelled Professional associations with page URL `/association-types/professional/`; the term slug stays `individual`.

## Launch steps

1. Publish the 48 case pages, 9951, containers 11013/11014/11249 and the 13 sub-landings. Strip " (new design)" from every title first: the card title is the page title.
2. JetEngine > Post Types > Cases: change the rewrite slug (for example `case-records`) and turn off Has archive, so pages own `/cases/` and `/cases/<slug>/`.
3. JetEngine > Taxonomies (all three): turn off Rewrite and Publicly queryable, so the sub-landing pages own `/service-types/<slug>/`, `/association-types/<slug>/`, `/association-industry/<slug>/`. Keep Show UI on.
4. Settings > Permalinks > Save (flush rewrites).
5. Run `launch-flip-status.js` in wp-admin (queries 11 to 24 to published only).
6. Redirection: 301 `/association-types/individual/` to `/association-types/professional/`.
7. Purge SG cache, then check `/cases/` filters, one case URL, and two sub-landings.

If launch is not a full staging-to-live push, the taxonomy, meta box, listing, query, filter and term-meta setup must be recreated on live and the IDs above change.
