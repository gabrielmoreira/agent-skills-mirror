# Route Selection

Use this reference when the `baseline` stage needs a clearer decision among attach, import, reproduce, and repair.

## Decision order

Prefer:

1. attach
2. import
3. reproduce
4. repair

But only when the chosen route still produces a trustworthy downstream reference.

## Route meanings

- `attach`:
  - reuse an already published and trustworthy baseline
- `import`:
  - bring a reusable baseline package or bundle into the current quest
- `reproduce`:
  - establish a baseline from source paper, repo, and evaluation path
- `repair`:
  - fix a bounded failure in an existing baseline line

## Questions to answer before choosing

- what exact baseline object are we using?
- what proof of trustworthiness already exists?
- what evidence is still missing?
- what is the cheapest credible next step?

## Route rejection logic

Reject a route if:

- provenance is weak
- metric or split compatibility is poor
- the cost is much higher than an equally trustworthy alternative
- the result would still be unusable downstream
