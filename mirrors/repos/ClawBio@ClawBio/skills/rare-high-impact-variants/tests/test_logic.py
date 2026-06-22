"""Domain-correctness tests for rare-high-impact-variants.

These verify the counting logic itself, not just the CLI contract: a variant is
counted only when it is carried, high-impact (loss-of-function) and rare.
"""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]
DEMO = SKILL_DIR / "demo_input.txt"


def _load():
    spec = spec_from_file_location("rhi", SKILL_DIR / "rare_high_impact_variants.py")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load()


@pytest.fixture(scope="module")
def demo_result(mod):
    return mod.run_analysis(mod.validate_input(DEMO))


def test_demo_counts_are_exact(demo_result):
    assert demo_result["variants_processed"] == 7
    assert demo_result["carried_variants"] == 6
    assert demo_result["high_impact_carried"] == 5
    # Only documented-rare variants count toward the headline (GENE1, GENE5, GENE7).
    assert demo_result["rare_high_impact_count"] == 3


def test_rarity_bands_sum_to_headline(demo_result):
    r = demo_result["by_rarity"]
    assert r == {"ultra_rare": 1, "rare": 2}
    assert sum(r.values()) == demo_result["rare_high_impact_count"]


def test_frequency_unknown_is_separated_not_counted_as_rare(demo_result):
    # GENE2 is a frameshift with no population frequency: high-impact, but not "rare".
    assert demo_result["high_impact_frequency_unknown"] == 1
    assert "GENE2" not in {f["gene"] for f in demo_result["findings"]}
    assert "GENE2" in demo_result["frequency_unknown_genes"]


def test_common_high_impact_counted_separately(demo_result):
    # GENE3 splice_donor AF 0.25 is high-impact but common.
    assert demo_result["high_impact_common"] == 1


def test_common_high_impact_is_excluded(demo_result):
    # GENE3 is a splice_donor (high-impact) but common (AF 0.25): high-impact, not rare.
    genes = {f["gene"] for f in demo_result["findings"]}
    assert "GENE3" not in genes


def test_missense_is_not_high_impact(demo_result):
    # GENE4 is a rare missense: rare but NOT loss-of-function, so excluded.
    genes = {f["gene"] for f in demo_result["findings"]}
    assert "GENE4" not in genes


def test_homref_is_not_carried(demo_result):
    # GENE6 is a rare frameshift but genotype 0/0: not carried.
    genes = {f["gene"] for f in demo_result["findings"]}
    assert "GENE6" not in genes


def test_stricter_threshold_drops_the_rare_band(mod):
    # At AF < 0.001 only GENE1 (0.0002) stays rare; GENE5 (0.004) and GENE7 (0.002)
    # become common; GENE2 remains frequency-unknown throughout.
    res = mod.run_analysis(mod.validate_input(DEMO), max_af=0.001)
    assert res["rare_high_impact_count"] == 1


def test_high_impact_term_matching(mod):
    assert mod._is_high_impact("SO:0001587|nonsense")
    assert mod._is_high_impact("SO:0001589|frameshift_variant")
    assert mod._is_high_impact("splice_acceptor_variant")
    assert not mod._is_high_impact("SO:0001583|missense_variant")
    assert not mod._is_high_impact("synonymous_variant")


def test_carried_and_zygosity(mod):
    assert mod._carries_alt("0/1") and mod._carries_alt("1/1") and mod._carries_alt("0|1")
    assert not mod._carries_alt("0/0") and not mod._carries_alt("./.")
    assert mod._zygosity("1/1") == "hom"
    assert mod._zygosity("0/1") == "het"


def test_empty_input_is_zero(mod, tmp_path):
    empty = tmp_path / "empty.vcf"
    empty.write_text("##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    res = mod.run_analysis(mod.validate_input(empty))
    assert res["rare_high_impact_count"] == 0
    assert res["carried_variants"] == 0
