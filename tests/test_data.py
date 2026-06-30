"""Tests for dataset.py — spec pair loading."""
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from intentspec.dataset import load_spec_pairs
from intentspec.schema import SpecPair


_EXAMPLE_PAIR = {
    "task_id": "T001",
    "spec_type": "algorithm",
    "ambiguous_prompt": "Sort a list.",
    "gold_prompt": "Sort ascending, preserve duplicates, no mutation.",
    "constraints": [
        {"id": "C1", "description": "Sorted", "test_code": "assert solution([2,1])==[1,2]"},
        {"id": "C2", "description": "No mutation", "test_code": "inp=[2,1];solution(inp);assert inp==[2,1]"},
    ],
    "stated_test_ids": ["C1"],
    "hidden_test_ids": ["C2"],
}


def _write_jsonl(path, entries: list[dict]) -> None:
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def test_load_spec_pairs_returns_list(tmp_path):
    p = tmp_path / "pairs.jsonl"
    _write_jsonl(p, [_EXAMPLE_PAIR])
    pairs = load_spec_pairs(p)
    assert isinstance(pairs, list)
    assert len(pairs) == 1


def test_load_spec_pairs_returns_spec_pair_objects(tmp_path):
    p = tmp_path / "pairs.jsonl"
    _write_jsonl(p, [_EXAMPLE_PAIR])
    pairs = load_spec_pairs(p)
    assert isinstance(pairs[0], SpecPair)


def test_load_spec_pairs_fields(tmp_path):
    p = tmp_path / "pairs.jsonl"
    _write_jsonl(p, [_EXAMPLE_PAIR])
    pair = load_spec_pairs(p)[0]
    assert pair.task_id == "T001"
    assert pair.spec_type == "algorithm"
    assert len(pair.constraints) == 2
    assert pair.stated_test_ids == ["C1"]
    assert pair.hidden_test_ids == ["C2"]


def test_load_spec_pairs_multiple_entries(tmp_path):
    p = tmp_path / "pairs.jsonl"
    second = {**_EXAMPLE_PAIR, "task_id": "T002", "spec_type": "data_transformation"}
    _write_jsonl(p, [_EXAMPLE_PAIR, second])
    pairs = load_spec_pairs(p)
    assert len(pairs) == 2
    assert pairs[1].task_id == "T002"
    assert pairs[1].spec_type == "data_transformation"


def test_load_spec_pairs_skips_blank_lines(tmp_path):
    p = tmp_path / "pairs.jsonl"
    with open(p, "w") as f:
        f.write(json.dumps(_EXAMPLE_PAIR) + "\n")
        f.write("\n")  # blank line
        f.write(json.dumps({**_EXAMPLE_PAIR, "task_id": "T002"}) + "\n")
    pairs = load_spec_pairs(p)
    assert len(pairs) == 2


def test_load_spec_pairs_invalid_json_raises(tmp_path):
    p = tmp_path / "pairs.jsonl"
    with open(p, "w") as f:
        f.write("not valid json\n")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_spec_pairs(p)


def test_load_spec_pairs_example_file():
    """Smoke-test the actual example file committed to the repo."""
    repo_root = os.path.join(os.path.dirname(__file__), "..")
    example_path = os.path.join(repo_root, "data", "specs", "spec_pairs.jsonl")
    if not os.path.exists(example_path):
        pytest.skip("data/specs/spec_pairs.jsonl not present")
    pairs = load_spec_pairs(example_path)
    assert len(pairs) >= 1
    for pair in pairs:
        assert pair.task_id
        assert pair.spec_type in ("algorithm", "data_transformation")
        assert pair.stated_test_ids
        assert pair.hidden_test_ids
