"""Validate the R2 experiment against the provided reference, not just itself."""

import pytest

from bonus.verification_ablation import run_unverified, run_verified
from lab8.db import init_store
from lab8.shapes.swarm_reference import run_claim
from tests.conftest import CLAIMS, WORLD


@pytest.mark.parametrize("claim_id", [f"C-{i:03d}" for i in range(1, 15)])
@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
def test_ablation_control_matches_reference(tmp_path, claim_id, seed):
    reference_db = tmp_path / "reference.sqlite"
    control_db = tmp_path / "control.sqlite"
    init_store(reference_db, WORLD, CLAIMS).close()
    init_store(control_db, WORLD, CLAIMS).close()
    reference = run_claim(claim_id, seed=seed, store_path=str(reference_db)).as_dict()
    control = run_unverified(claim_id, seed=seed, store_path=str(control_db)).as_dict()
    for field in ("run_id", "shape", "trace_path"):
        reference.pop(field)
        control.pop(field)
    assert control == reference


def test_verification_stops_the_known_wrongful_refund(public_db):
    result = run_verified("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
