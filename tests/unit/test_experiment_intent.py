"""Laboratory intent must never imply an approved operator command."""
import pytest

from lab.studies.common.experiment_intent import (
    ExperimentIntent, RequestedOperation, describe_intent,
)


def valid(**overrides):
    fields = dict(
        protocol_id="protocol-1",
        experiment_id="experiment-1",
        target_domain="world",
        operation=RequestedOperation.PREPARE,
        contract_ref="world.contract.v1",
        requested_by="lab-operator",
    )
    fields.update(overrides)
    return ExperimentIntent(**fields)


def test_intent_does_not_authorize_execution():
    result = describe_intent(valid(operation=RequestedOperation.INTERVENE))
    assert result["status"] == "unapproved_intent"
    assert result["operation"] == "intervene"
    assert "authorization" not in result


@pytest.mark.parametrize("domain", ["lab", "frontend", "observation", "invalid"])
def test_no_observation_or_consumer_as_causal_target(domain):
    with pytest.raises(ValueError, match="permitted domain"):
        valid(target_domain=domain)


def test_reject_implicit_operation_and_missing_contract():
    with pytest.raises(ValueError, match="explicit"):
        valid(operation="run")
    with pytest.raises(ValueError, match="contract_ref"):
        valid(contract_ref=" ")
