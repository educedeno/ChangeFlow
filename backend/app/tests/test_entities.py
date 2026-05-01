import pytest
from uuid import uuid4

from app.domain.entities import Approval, Decision
from app.domain.enums import ApprovalStatus, DecisionAction


class TestApproval:
    def test_approval_starts_pending(self):
        approval = Approval(request_id=uuid4(), reviewer_id=uuid4())
        assert approval.status == ApprovalStatus.PENDING
        assert approval.is_pending()
        assert approval.decided_at is None

    def test_mark_approved_changes_status(self):
        approval = Approval(request_id=uuid4(), reviewer_id=uuid4())
        approval.mark_approved()
        assert approval.status == ApprovalStatus.APPROVED
        assert approval.decided_at is not None

    def test_cannot_approve_twice(self):
        approval = Approval(request_id=uuid4(), reviewer_id=uuid4())
        approval.mark_approved()
        with pytest.raises(ValueError):
            approval.mark_approved()

    def test_cannot_reject_already_approved(self):
        approval = Approval(request_id=uuid4(), reviewer_id=uuid4())
        approval.mark_approved()
        with pytest.raises(ValueError):
            approval.mark_rejected()


class TestDecision:
    def test_approve_decision_does_not_require_comment(self):
        decision = Decision(approval_id=uuid4(), action=DecisionAction.APPROVE)
        assert decision.action == DecisionAction.APPROVE

    def test_reject_decision_requires_comment(self):
        with pytest.raises(ValueError):
            Decision(approval_id=uuid4(), action=DecisionAction.REJECT)

    def test_request_changes_requires_comment(self):
        with pytest.raises(ValueError):
            Decision(
                approval_id=uuid4(),
                action=DecisionAction.REQUEST_CHANGES,
                comment="   "  # solo espacios tampoco vale
            )

    def test_reject_with_valid_comment_works(self):
        decision = Decision(
            approval_id=uuid4(),
            action=DecisionAction.REJECT,
            comment="Falta plan de rollback"
        )
        assert decision.comment == "Falta plan de rollback"