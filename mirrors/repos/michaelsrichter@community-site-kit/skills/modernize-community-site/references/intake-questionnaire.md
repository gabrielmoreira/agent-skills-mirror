# Intake questionnaire (one conversation, about 15 minutes)

Ask these in one go (or with `ask_user`, one question at a time). Record answers in `docs/decision-log.md`.
If the owner is unavailable, use the default in brackets and say so in the first update email.

## The organization

1. Full name, short name for labels ("Riverbend event"), legal name for the footer. [from the old site]
2. Region served (used in headings and SEO, e.g. "Long Island", "the Hudson Valley"). [from the old site]
3. Old website address(es). Are there pages or PDFs that are not linked from the menu? [crawl from home]
4. Hotline/phone, email, mailing address, Facebook group/page, Instagram, newsletter sign-up link. [from the old site]
5. Recurring event pattern (e.g. "every Tuesday: lesson 7:30, dancing 8–10:30") and prices
   (member / non-member / student). [from the old site; mark for review]

## Accounts and hosting

6. Which GitHub account or organization should own the repository? Public or private? [owner's personal account, public]
   - Note: employer-managed (EMU) GitHub accounts cannot be invited to personal repos. Editors need personal accounts.
7. Which Azure subscription? Any existing resources for this organization? [current `az` default; Free plan]
8. Custom domain now or later? Which registrar (Namecheap, GoDaddy, Google/Squarespace, Cloudflare)? [later; use the azurestaticapps.net address]
9. Who will edit content? Their GitHub usernames (to invite as collaborators). [owner only]

## Content and media

10. Where are your own photos and videos? Please put the best ones in one folder and tell me the path.
    Who took them, and do we have permission to post them? [use openly licensed photos with credit until confirmed]
11. Do you want a rotating photo slideshow on the homepage? [yes, accessible, real dancing photos]
12. Do you want an announcement banner (weather, closures)? [no; editors can turn one on]
13. Community sources to include: regional dance calendars (often monthly PDFs), Facebook groups,
    teachers' own calendars, other organizers' sites. Geographic limits? [region + nearby city swing events]
14. Teachers, bands and DJs you work with — any websites or social pages you know of? [search for them]

## Communication and analytics

15. How should I tell you when something is live — email or Teams? Which address? [email]
16. Google Analytics 4 measurement ID and Microsoft Clarity project ID? Consent: opt-in or opt-out? [add later; opt-in]
17. Anything you dislike on similar sites? Colors or style you like? [warm, cheerful, readable]

## Always tell the owner up front

- Their manual steps will be: approving GitHub OAuth app creation in a signed-in browser (or doing it
  themselves), adding DNS records at the registrar, and confirming photo permissions.
- Every request they make will be built, tested, deployed and reported back by email.
