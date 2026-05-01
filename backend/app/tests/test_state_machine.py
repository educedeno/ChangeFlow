import pytest

from app.domain.enums import RequestStatus, RiskLevel
from app.domain.exceptions import (
    InvalidStateTransitionError,
    BusinessRuleViolationError,
)
from app.domain.state_machine import (
    DraftState,
    SubmittedState,
    InReviewState,
    ChangesRequestedState,
    ApprovedState,
    RejectedState,
    CompletedState,
    ChangeRequestContext,
    state_from_status,
)


# ---------------------------------------------------------------------------
# DraftState
# ---------------------------------------------------------------------------

class TestDraftState:
    def test_low_risk_can_submit(self):
        state = DraftState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        new_state = state.submit(ctx)
        assert isinstance(new_state, SubmittedState)

    def test_high_risk_without_rollback_cannot_submit(self):
        state = DraftState()
        ctx = ChangeRequestContext(
            risk_level=RiskLevel.HIGH, has_rollback_plan=False
        )
        with pytest.raises(BusinessRuleViolationError):
            state.submit(ctx)

    def test_high_risk_with_rollback_can_submit(self):
        state = DraftState()
        ctx = ChangeRequestContext(
            risk_level=RiskLevel.HIGH, has_rollback_plan=True
        )
        new_state = state.submit(ctx)
        assert isinstance(new_state, SubmittedState)

    def test_cannot_approve_from_draft(self):
        state = DraftState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        with pytest.raises(InvalidStateTransitionError):
            state.approve(ctx)


# ---------------------------------------------------------------------------
# SubmittedState
# ---------------------------------------------------------------------------

class TestSubmittedState:
    def test_can_start_review(self):
        state = SubmittedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        assert isinstance(state.start_review(ctx), InReviewState)

    def test_can_reject_from_submitted(self):
        state = SubmittedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        assert isinstance(state.reject(ctx), RejectedState)

    def test_cannot_approve_from_submitted(self):
        state = SubmittedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        with pytest.raises(InvalidStateTransitionError):
            state.approve(ctx)


# ---------------------------------------------------------------------------
# InReviewState
# ---------------------------------------------------------------------------

class TestInReviewState:
    def test_low_risk_one_approval_enough(self):
        state = InReviewState()
        ctx = ChangeRequestContext(
            risk_level=RiskLevel.LOW, approvals_count=1
        )
        assert isinstance(state.approve(ctx), ApprovedState)

    def test_high_risk_one_approval_not_enough(self):
        state = InReviewState()
        ctx = ChangeRequestContext(
            risk_level=RiskLevel.HIGH, approvals_count=1
        )
        with pytest.raises(BusinessRuleViolationError):
            state.approve(ctx)

    def test_high_risk_two_approvals_succeeds(self):
        state = InReviewState()
        ctx = ChangeRequestContext(
            risk_level=RiskLevel.HIGH, approvals_count=2
        )
        assert isinstance(state.approve(ctx), ApprovedState)

    def test_can_reject(self):
        state = InReviewState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.MEDIUM)
        assert isinstance(state.reject(ctx), RejectedState)

    def test_can_request_changes(self):
        state = InReviewState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.MEDIUM)
        assert isinstance(state.request_changes(ctx), ChangesRequestedState)


# ---------------------------------------------------------------------------
# ChangesRequestedState
# ---------------------------------------------------------------------------

class TestChangesRequestedState:
    def test_can_resubmit(self):
        state = ChangesRequestedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        assert isinstance(state.submit(ctx), SubmittedState)


# ---------------------------------------------------------------------------
# Estados terminales
# ---------------------------------------------------------------------------

class TestTerminalStates:
    def test_rejected_cannot_transition(self):
        state = RejectedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        with pytest.raises(InvalidStateTransitionError):
            state.submit(ctx)
        with pytest.raises(InvalidStateTransitionError):
            state.approve(ctx)

    def test_completed_cannot_transition(self):
        state = CompletedState()
        ctx = ChangeRequestContext(risk_level=RiskLevel.LOW)
        with pytest.raises(InvalidStateTransitionError):
            state.approve(ctx)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestStateFactory:
    def test_rebuild_state_from_status(self):
        assert isinstance(state_from_status(RequestStatus.DRAFT), DraftState)
        assert isinstance(
            state_from_status(RequestStatus.IN_REVIEW), InReviewState
        )
        assert isinstance(
            state_from_status(RequestStatus.APPROVED), ApprovedState
        )