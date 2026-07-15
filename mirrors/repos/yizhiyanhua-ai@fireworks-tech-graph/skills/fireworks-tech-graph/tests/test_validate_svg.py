from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_svg.py"
SPEC = importlib.util.spec_from_file_location("validate_svg", SCRIPT)
assert SPEC and SPEC.loader
validate_svg = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_svg
SPEC.loader.exec_module(validate_svg)


class ValidateSvgTest(unittest.TestCase):
    def write_svg(self, body: str, root_attrs: str = "") -> Path:
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        path = Path(tempdir.name) / "diagram.svg"
        path.write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" {root_attrs}>'
            '<defs><marker id="arrow-main"><path d="M0 0 L8 4 L0 8 Z"/></marker></defs>'
            f"{body}</svg>",
            encoding="utf-8",
        )
        return path

    def test_text_with_equals_is_valid_xml(self) -> None:
        path = self.write_svg('<text x="10" y="20">retrieve(top_k=5)</text>')
        ok, details = validate_svg.run_check(path, "xml")
        self.assertTrue(ok, details)

    def test_marker_start_and_end_are_resolved_structurally(self) -> None:
        path = self.write_svg(
            '<path d="M 20 20 H 100" marker-start="url(#arrow-main)" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "markers")
        self.assertTrue(ok, details)

    def test_missing_marker_start_is_reported(self) -> None:
        path = self.write_svg('<path d="M 20 20 H 100" marker-start="url(#missing)"/>')
        ok, details = validate_svg.run_check(path, "markers")
        self.assertFalse(ok)
        self.assertEqual(details, ["missing marker: missing"])

    def test_absolute_hv_path_collision_is_reported(self) -> None:
        path = self.write_svg(
            '<rect id="blocker" x="160" y="80" width="80" height="60"/>'
            '<path id="edge" d="M 20 110 H 280 V 180" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)
        self.assertIn("path#edge intersects rect#blocker", details)

    def test_relative_hv_path_collision_is_reported(self) -> None:
        path = self.write_svg(
            '<rect id="blocker" x="160" y="80" width="80" height="60"/>'
            '<path id="edge" d="m 20 110 h 260 v 70" marker-end="url(#arrow-main)"/>'
        )
        ok, _ = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)

    def test_quadratic_and_cubic_curves_are_sampled(self) -> None:
        quadratic = self.write_svg(
            '<rect id="blocker" x="160" y="80" width="80" height="60"/>'
            '<path id="edge" d="M 20 180 Q 200 20 380 180" marker-end="url(#arrow-main)"/>'
        )
        cubic = self.write_svg(
            '<rect id="blocker" x="160" y="80" width="80" height="60"/>'
            '<path id="edge" d="M 20 180 C 100 60 300 60 380 180" marker-end="url(#arrow-main)"/>'
        )
        self.assertFalse(validate_svg.run_check(quadratic, "collisions")[0])
        self.assertFalse(validate_svg.run_check(cubic, "collisions")[0])

    def test_elliptical_arc_is_sampled_instead_of_reduced_to_its_chord(self) -> None:
        path = self.write_svg(
            '<rect id="blocker" x="160" y="15" width="80" height="40"/>'
            '<path id="edge" d="M 20 180 A 180 160 0 0 1 380 180" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)
        self.assertIn("path#edge intersects rect#blocker", details)

    def test_boundary_to_boundary_connection_is_not_a_collision(self) -> None:
        path = self.write_svg(
            '<rect id="source" x="20" y="80" width="80" height="60"/>'
            '<rect id="target" x="280" y="80" width="80" height="60"/>'
            '<path id="edge" d="M 100 110 H 280" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertTrue(ok, details)

    def test_small_dashed_node_is_an_obstacle_but_large_container_is_not(self) -> None:
        path = self.write_svg(
            '<rect id="container" x="10" y="20" width="380" height="200" fill="none" stroke-dasharray="6 4"/>'
            '<rect id="node" x="160" y="80" width="80" height="60" fill="none" stroke-dasharray="4 3"/>'
            '<path id="edge" d="M 20 110 H 280" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)
        self.assertEqual(details, ["path#edge intersects rect#node"])

    def test_legend_sample_arrows_do_not_collide_with_their_background(self) -> None:
        path = self.write_svg(
            '<rect id="legend" x="20" y="150" width="200" height="70"/>'
            '<path id="sample-a" d="M 40 170 H 80" marker-end="url(#arrow-main)"/>'
            '<path id="sample-b" d="M 40 195 H 80" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertTrue(ok, details)

    def test_legacy_legend_remains_an_obstacle_for_business_edges(self) -> None:
        path = self.write_svg(
            '<rect id="legend" x="200" y="150" width="180" height="70"/>'
            '<path id="sample-a" d="M 220 170 H 260" marker-end="url(#arrow-main)"/>'
            '<path id="sample-b" d="M 220 195 H 260" marker-end="url(#arrow-main)"/>'
            '<path id="business" d="M 300 20 V 190 H 100" marker-end="url(#arrow-main)"/>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)
        self.assertIn("path#business intersects rect#legend", details)

    def test_group_transform_is_applied_to_paths_and_obstacles(self) -> None:
        path = self.write_svg(
            '<g transform="translate(80 20)">'
            '<rect id="blocker" x="80" y="60" width="80" height="60"/>'
            '<path id="edge" d="M 20 90 H 200" marker-end="url(#arrow-main)"/>'
            '</g>'
        )
        ok, details = validate_svg.run_check(path, "collisions")
        self.assertFalse(ok)
        self.assertEqual(details, ["path#edge intersects rect#blocker"])

    def test_showcase_composition_rejects_more_than_two_bends(self) -> None:
        path = self.write_svg(
            '<path id="zigzag" data-graph-role="edge" d="M 20 20 H 80 V 60 H 140 V 120" '
            'marker-end="url(#arrow-main)"/>',
            'data-quality-profile="showcase"',
        )
        ok, details = validate_svg.run_check(path, "composition")
        self.assertFalse(ok)
        self.assertTrue(any("edge_bend_budget" in detail for detail in details), details)

    def test_showcase_composition_rejects_tight_node_spacing(self) -> None:
        path = self.write_svg(
            '<rect id="lane" data-graph-role="container" x="10" y="10" width="380" height="210"/>'
            '<rect id="first" data-graph-role="node" x="40" y="70" width="80" height="60"/>'
            '<rect id="second" data-graph-role="node" x="140" y="70" width="80" height="60"/>',
            'data-quality-profile="showcase"',
        )
        ok, details = validate_svg.run_check(path, "composition")
        self.assertFalse(ok)
        self.assertTrue(any("node_gap" in detail for detail in details), details)

    def test_composition_detects_near_miss_label_clearance(self) -> None:
        path = self.write_svg(
            '<path id="flow" data-graph-role="edge" d="M 20 100 H 380" marker-end="url(#arrow-main)"/>'
            '<text id="near" data-graph-role="label" data-owner="other" x="200" y="94" '
            'text-anchor="middle" font-size="12">near miss</text>',
            'data-quality-profile="standard" data-min-label-clearance="4"',
        )
        geometry_ok, geometry_details = validate_svg.run_check(path, "geometry")
        self.assertTrue(geometry_ok, geometry_details)
        composition_ok, composition_details = validate_svg.run_check(path, "composition")
        self.assertFalse(composition_ok)
        self.assertTrue(any("label_clearance" in detail for detail in composition_details), composition_details)

    def test_dark_luxury_fixture_passes_the_same_composition_gate(self) -> None:
        fixture = SCRIPT.parents[1] / "fixtures" / "dark-luxury-style8.svg"
        ok, details = validate_svg.run_check(fixture, "composition")
        self.assertTrue(ok, details)


if __name__ == "__main__":
    unittest.main()
