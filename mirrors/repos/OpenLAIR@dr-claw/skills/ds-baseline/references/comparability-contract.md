# Comparability Contract

Use this reference when deciding whether a baseline is truly usable downstream.

## Minimum contract

Make these fields explicit:

- task identity
- dataset identity
- dataset version
- split contract
- preprocessing boundary
- evaluation script or path
- required metric keys
- metric directions
- seed policy if relevant
- source commit or package identity
- known deviations

## Verdict logic

- `verified`:
  - comparison contract is stable enough for downstream work
- `partially_verified`:
  - mostly usable, but caveats must travel with it
- `operational_but_incomparable`:
  - the system runs, but later stages should not treat it as a clean comparison
- `failed`:
  - not suitable as a baseline

If later `experiment` work would have to keep guessing the comparison contract, the baseline is not ready.
