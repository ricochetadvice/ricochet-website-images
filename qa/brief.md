You are doing an independent QA review of the newly launched website ricochetadvice.com (Ricochet, a consultancy for professional and trade associations). The attached JSON has every live page (excluding student course-resource pages): URL, title tag, meta description, robots, H1 count, FAQ question count, and the visible text of the main content (truncated to 6000 chars).

House rules the site must follow:
- No em dashes. Never the words "leverage" or "seamless".
- Brand is "Ricochet" (alternate "Ricochet Association Transformation"); never "Ricochet Advice".
- Never mention Make (automation platform), ASDSO, or C-SPAN. Exception: the AMS Connector terms of service page may list Make.ai as a subprocessor.
- Chris Gloede's title is Chief Consultant, never Founder. He is "first CMO of the American Bar Association".
- Public phone is (202) 240-8752. Booking goes to meetings.hubspot.com/chrisg/meet-with-chris, never schedulechris.com.
- No prices on service pages (HubSpot, Mailchimp, Services). Academy course pages may show prices.
- Service names: Member Research, Membership Modeling, Marketing Studio (renamed today from "Brand and Campaign Studio"), Tech and AI Roadmaps, Fractional Staffing and Training; HubSpot pages: Implementation, AMS Connector, Evolution Coaching, Preferences Portal, Sales Partnership; Mailchimp: Implementation, AMS Connector, Evolution Coaching.
- HubSpot partner tier is "Platinum Agency Partner". Mailchimp status is "Mailchimp Pro Partner".
- Samples use the fictional "American Widget Society".
- Headlines are questions in first person singular ("How do I", "my association").
- Thank-you, form, legal and utility pages should be noindex.

Already verified by an automated crawl (you do not need to re-check): every page returns 200, no broken internal links or images, no redirect chains, sitemap has only indexable pages, JSON-LD parses on every page, FAQ schema counts match the on-page accordions, all external links open in a new tab, no schedulechris.com links, mobile pages do not scroll sideways, banned words and em dashes absent.

Your job: find what the crawl cannot. Look for:
1. Factual contradictions between pages (numbers, weeks, years in business, counts of clients or case studies, credits, prices, dates, names, titles).
2. Copy errors: typos, grammar, broken sentences, leftover placeholder or draft text, duplicated paragraphs, text that reads like internal notes.
3. Naming inconsistencies with the rules above (old service names, wrong partner tier, wrong title).
4. SEO problems: weak, duplicate or mismatched titles and meta descriptions, pages that should be noindex but are not (or the reverse).
5. Anything an association executive would find confusing or unprofessional.

Output: a numbered list of concrete findings only, most important first. For each: URL, the exact problem text quoted (under 20 words), why it is a problem, and the fix. Skip anything you are not confident about. Do not list things that are fine. If you find nothing in a category, say so in one line.
