"""Tests de casos de uso usando repositorios fake en memoria."""

from typing import Optional, List
from uuid import UUID, uuid4

import pytest

from app.application.use_cases.approve_request import ApproveRequestUseCase
from app.application.use_cases.reject_request import RejectRequestUseCase
from app.application.use_cases.assign_reviewer import AssignReviewerUseCase
from app.domain.entities import Approval, Decision
from app.domain.enums import ApprovalStatus, RequestStatus, RiskLevel
from app.domain.repositories import ApprovalRepository, ChangeRequestRepository


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

class FakeApprovalRepository(ApprovalRepository):
    def __init__(self):
        self.approvals: dict[UUID, Approval] = {}
        self.decisions: List[Decision] = []

    def get_by_id(self, approval_id: UUID) -> Optional[Approval]:
        return self.approvals.get(approval_id)

    def list_by_request(self, request_id: UUID) -> List[Approval]:
        return [a for a in self.approvals.values() if a.request_id == request_id]

    def list_pending_for_reviewer(self, reviewer_id: UUID) -> List[Approval]:
        return [
            a for a in self.approvals.values()
            if a.reviewer_id == reviewer_id and a.is_pending()
        ]

    def save(self, approval: Approval) -> Approval:
        self.approvals[approval.id] = approval
        return approval

    def save_decision(self, decision: Decision) -> Decision:
        self.decisions.append(decision)
        return decision

    def count_approved_for_request(self, request_id: UUID) -> int:
        return sum(
            1 for a in self.approvals.values()
            if a.request_id == request_id and a.status == ApprovalStatus.APPROVED
        )


class FakeChangeRequestRepository(ChangeRequestRepository):
    def __init__(
        self,
        request_id: UUID,
        status: RequestStatus,
        risk_level: RiskLevel,
        has_rollback: bool = True,
    ):
        self.request_id = request_id
        self.status = status
        self.risk_level = risk_level
        self.has_rollback = has_rollback

    def get_status(self, request_id: UUID):
        return self.status if request_id == self.request_id else None

    def update_status(self, request_id: UUID, new_status) -> None:
        self.status = new_status

    def get_risk_level(self, request_id: UUID):
        return self.risk_level if request_id == self.request_id else None

    def has_rollback_plan(self, request_id: UUID) -> bool:
        return self.has_rollback


# ---------------------------------------------------------------------------
# ApproveRequestUseCase
# ---------------------------------------------------------------------------

class TestApproveRequest:
    def test_low_risk_single_approval_completes_request(self):
        request_id = uuid4()
        reviewer_id = uuid4()
        approval = Approval(request_id=request_id, reviewer_id=reviewer_id)

        approval_repo = FakeApprovalRepository()
        approval_repo.save(approval)
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.IN_REVIEW,
            risk_level=RiskLevel.LOW,
        )

        use_case = ApproveRequestUseCase(approval_repo, request_repo)
        result = use_case.run(approval.id, reviewer_id)

        assert result.success
        assert request_repo.status == RequestStatus.APPROVED

    def test_high_risk_first_approval_does_not_complete(self):
        request_id = uuid4()
        reviewer_id_1 = uuid4()
        approval = Approval(request_id=request_id, reviewer_id=reviewer_id_1)

        approval_repo = FakeApprovalRepository()
        approval_repo.save(approval)
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.IN_REVIEW,
            risk_level=RiskLevel.HIGH,
        )

        use_case = ApproveRequestUseCase(approval_repo, request_repo)
        result = use_case.run(approval.id, reviewer_id_1)

        assert result.success
        assert request_repo.status == RequestStatus.IN_REVIEW  # sigue en review

    def test_unauthorized_reviewer_rejected(self):
        request_id = uuid4()
        actual_reviewer = uuid4()
        intruder = uuid4()
        approval = Approval(request_id=request_id, reviewer_id=actual_reviewer)

        approval_repo = FakeApprovalRepository()
        approval_repo.save(approval)
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.IN_REVIEW,
            risk_level=RiskLevel.LOW,
        )

        use_case = ApproveRequestUseCase(approval_repo, request_repo)
        result = use_case.run(approval.id, intruder)

        assert not result.success
        assert "autorizado" in result.message.lower()


# ---------------------------------------------------------------------------
# RejectRequestUseCase
# ---------------------------------------------------------------------------

class TestRejectRequest:
    def test_reject_requires_comment(self):
        request_id = uuid4()
        reviewer_id = uuid4()
        approval = Approval(request_id=request_id, reviewer_id=reviewer_id)

        approval_repo = FakeApprovalRepository()
        approval_repo.save(approval)
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.IN_REVIEW,
            risk_level=RiskLevel.LOW,
        )

        use_case = RejectRequestUseCase(approval_repo, request_repo)
        result = use_case.run(approval.id, reviewer_id, comment="")

        assert not result.success
        assert "comentario" in result.message.lower()

    def test_reject_transitions_request_to_rejected(self):
        request_id = uuid4()
        reviewer_id = uuid4()
        approval = Approval(request_id=request_id, reviewer_id=reviewer_id)

        approval_repo = FakeApprovalRepository()
        approval_repo.save(approval)
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.IN_REVIEW,
            risk_level=RiskLevel.HIGH,
        )

        use_case = RejectRequestUseCase(approval_repo, request_repo)
        result = use_case.run(
            approval.id, reviewer_id, comment="Falta plan de rollback"
        )

        assert result.success
        assert request_repo.status == RequestStatus.REJECTED


# ---------------------------------------------------------------------------
# AssignReviewerUseCase
# ---------------------------------------------------------------------------

class TestAssignReviewer:
    def test_assign_low_risk_one_reviewer_ok(self):
        request_id = uuid4()
        reviewer_id = uuid4()

        approval_repo = FakeApprovalRepository()
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.SUBMITTED,
            risk_level=RiskLevel.LOW,
        )

        use_case = AssignReviewerUseCase(approval_repo, request_repo)
        result = use_case.run(request_id, reviewer_id)

        assert result.success
        assert len(approval_repo.list_by_request(request_id)) == 1

    def test_assign_high_risk_allows_two_reviewers(self):
        request_id = uuid4()
        reviewer_a = uuid4()
        reviewer_b = uuid4()

        approval_repo = FakeApprovalRepository()
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.SUBMITTED,
            risk_level=RiskLevel.HIGH,
        )

        use_case = AssignReviewerUseCase(approval_repo, request_repo)
        assert use_case.run(request_id, reviewer_a).success
        assert use_case.run(request_id, reviewer_b).success
        assert len(approval_repo.list_by_request(request_id)) == 2

    def test_cannot_exceed_policy_limit(self):
        request_id = uuid4()
        approval_repo = FakeApprovalRepository()
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.SUBMITTED,
            risk_level=RiskLevel.LOW,  # solo permite 1
        )

        use_case = AssignReviewerUseCase(approval_repo, request_repo)
        assert use_case.run(request_id, uuid4()).success
        result = use_case.run(request_id, uuid4())  # segundo intento
        assert not result.success
        assert "policy" in result.message.lower() or "máximo" in result.message.lower()

    def test_cannot_assign_same_reviewer_twice(self):
        request_id = uuid4()
        reviewer_id = uuid4()
        approval_repo = FakeApprovalRepository()
        request_repo = FakeChangeRequestRepository(
            request_id=request_id,
            status=RequestStatus.SUBMITTED,
            risk_level=RiskLevel.HIGH,
        )

        use_case = AssignReviewerUseCase(approval_repo, request_repo)
        assert use_case.run(request_id, reviewer_id).success
        result = use_case.run(request_id, reviewer_id)
        assert not result.success