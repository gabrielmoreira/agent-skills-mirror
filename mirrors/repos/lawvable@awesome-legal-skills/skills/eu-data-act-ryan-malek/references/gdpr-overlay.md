# GDPR overlay — interaction with personal data

The Data Act does not override the GDPR. Article 1(5) is the bridge clause; Recital 7 and FAQ Q25a govern the practical interaction.

## Article 1(5) — verbatim

> "This Regulation is without prejudice to Union and national legal acts on the protection of personal data, privacy and confidentiality of communications and the integrity of terminal equipment, which apply to personal data processed in connection with the rights and obligations laid down in this Regulation, in particular Regulations (EU) 2016/679 and (EU) 2018/1725 and Directives 2002/58/EC and (EU) 2016/680, including the powers and competence of supervisory authorities and the rights of data subjects. To the extent that users are data subjects, the rights laid down in Chapter II of this Regulation shall complement the rights of access by data subjects and to data portability under Articles 15 and 20 of Regulation (EU) 2016/679. In the event of a conflict between this Regulation and Union law on the protection of personal data or privacy, or national legislation adopted in accordance with such Union law, the relevant Union or national law on the protection of personal data or privacy shall prevail."

## Two scenarios

### A. The user IS the data subject

When the same person who is the Data Act "user" is also the natural person whose personal data is being requested:

- A Data Act Article 4 request resembles a GDPR Article 15 access request.
- A Data Act Article 5 third-party transfer request resembles a GDPR Article 20 portability request.
- The existing GDPR legal basis used for the original processing continues to apply; the Data Act adds an additional channel for access, not a new basis.
- Practical effect: self-service export is usually fine. Standard GDPR data-subject identification controls are sufficient.

### B. The user is NOT the data subject

When the user is, for example, an employer requesting data that includes employee personal data, or an owner-lessor requesting data generated while a renter was the operator:

- **The Data Act is NOT a GDPR Article 6 legal basis** (Recital 7; FAQ Q25a, non-authoritative).
- The data holder must establish a separate Article 6 basis — typically (b) contract necessity, (c) legal obligation, (e) public interest task, or (f) legitimate interest balancing — OR provide anonymised data.
- The disclosure may need to be conditioned, redacted, or replaced with aggregate / anonymised information.
- Practical effect: treat as a privacy review trigger; do not auto-release.

## FAQ extracts (non-authoritative)

### Q25a — Legal bases for replying to a request

The FAQ distinguishes three operational scenarios:
- User = data subject: Data Act request resembles GDPR Art. 15 / 20 access.
- User ≠ data subject: data holder must assess legal basis or provide anonymised data; possible bases include contract necessity, service / legitimate interests of data holder or third party.
- Data is shared between two controllers: each must demonstrate own GDPR compliance under the accountability principle.

### Q25b — Verifying the requester's GDPR legal basis

When data is shared between two controllers, each must be able to demonstrate their own GDPR compliance. They should cooperate to share strictly necessary information to allow each to demonstrate compliance.

## Data Act mechanics that interact with GDPR

| Data Act provision | Interaction |
|--------------------|-------------|
| Art. 3(2)(d) erasure | Independent of, but consistent with, GDPR Art. 17 erasure rights |
| Art. 3(3)(c) data-holder use disclosure | Must be consistent with GDPR Art. 13/14 transparency |
| Art. 4(1) free of charge | Aligns with GDPR Art. 12(5) |
| Art. 4(1) without undue delay | Distinct from GDPR's one-month default; see `references/gotchas.md` item 17 |
| Art. 4(2) safety carve-out | Does not displace GDPR Art. 6 / Art. 9 special-categories analysis |
| Art. 4(6)–(8), 5(9)–(11) trade-secret regime | Does not override GDPR data-subject rights (per Recital 31 final sentence) |
| Art. 5 third-party transfer | If personal data, GDPR Art. 6 basis required separately by the third party as recipient |

## Recital 31 final sentence — important

> "The exceptions to data access rights in this Regulation should not in any case limit the right of access and right to data portability of data subjects under Regulation (EU) 2016/679."

Trade-secret refusal does not extend to GDPR-Article-15/20 rights of data subjects.

## Working principle for outputs

When personal data is involved, the deliverable surfaces:
1. Whether the requester is the data subject (Case A) or not (Case B).
2. If Case B, the Article 6 GDPR legal basis the data holder will rely on, OR the anonymisation approach.
3. Whether GDPR Article 9 special categories are involved.
4. Whether the third-party recipient (if any) has its own GDPR compliance posture.
5. Whether ePrivacy / national overlay applies (terminal-equipment provisions for IoT data may engage Directive 2002/58/EC).
