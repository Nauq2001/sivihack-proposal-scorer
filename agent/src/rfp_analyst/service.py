from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from .criteria import resolve_user_criterion
from .models import (
    CriteriaStateSnapshot,
    CriterionPacket,
    CriterionWeight,
    RFPAnalysis,
    ScoringInput,
    UserCriterionInput,
)
from .validation import validate_analysis


class StateError(ValueError):
    pass


@dataclass
class CriteriaState:
    analysis: RFPAnalysis
    raw_rfp_text: str
    criteria: list[CriterionWeight]
    packets: list[CriterionPacket]
    revision: int = 1

    @classmethod
    def from_analysis(cls, analysis: RFPAnalysis, raw_rfp_text: str) -> "CriteriaState":
        validate_analysis(analysis, raw_rfp_text)
        return cls(
            analysis=deepcopy(analysis),
            raw_rfp_text=raw_rfp_text,
            criteria=deepcopy(analysis.suggested_criteria_weights),
            packets=deepcopy(analysis.criterion_packets),
        )

    @classmethod
    def from_snapshot(cls, snapshot: CriteriaStateSnapshot) -> "CriteriaState":
        validate_analysis(snapshot.analysis, snapshot.raw_rfp_text)
        if {item.name for item in snapshot.confirmed_criteria} != {
            item.criterion_name for item in snapshot.criterion_packets
        }:
            raise StateError("PACKET_MISMATCH")
        return cls(
            analysis=deepcopy(snapshot.analysis),
            raw_rfp_text=snapshot.raw_rfp_text,
            criteria=deepcopy(snapshot.confirmed_criteria),
            packets=deepcopy(snapshot.criterion_packets),
            revision=snapshot.revision,
        )

    def to_snapshot(self) -> CriteriaStateSnapshot:
        return CriteriaStateSnapshot(
            revision=self.revision,
            raw_rfp_text=self.raw_rfp_text,
            analysis=deepcopy(self.analysis),
            confirmed_criteria=deepcopy(self.criteria),
            criterion_packets=deepcopy(self.packets),
        )

    def add_or_merge(self, user_input: UserCriterionInput, resolver=None):
        resolved = resolve_user_criterion(
            user_input,
            self.criteria,
            self.packets,
            self.analysis.requirements,
            self.raw_rfp_text,
            resolver,
        )
        if resolved.is_duplicate:
            index = next(i for i, item in enumerate(self.criteria) if item.name == resolved.criterion.name)
            self.criteria[index] = resolved.criterion
        else:
            self.criteria.append(resolved.criterion)
            self.packets.append(resolved.packet)
        self.revision += 1
        return resolved

    def remove(self, criterion_name: str) -> None:
        self.criteria = [item for item in self.criteria if item.name != criterion_name]
        self.packets = [item for item in self.packets if item.criterion_name != criterion_name]
        self.revision += 1

    def edit(self, criterion_name: str, user_input: UserCriterionInput, resolver=None):
        if not any(item.name == criterion_name for item in self.criteria):
            raise StateError("CRITERION_NOT_FOUND")
        remaining_criteria = [item for item in self.criteria if item.name != criterion_name]
        remaining_packets = [item for item in self.packets if item.criterion_name != criterion_name]
        resolved = resolve_user_criterion(
            user_input,
            remaining_criteria,
            remaining_packets,
            self.analysis.requirements,
            self.raw_rfp_text,
            resolver,
        )
        if resolved.is_duplicate:
            index = next(
                i for i, item in enumerate(remaining_criteria) if item.name == resolved.criterion.name
            )
            remaining_criteria[index] = resolved.criterion
        else:
            remaining_criteria.append(resolved.criterion)
            remaining_packets.append(resolved.packet)
        self.criteria = remaining_criteria
        self.packets = remaining_packets
        self.revision += 1
        return resolved

    def package(self, raw_proposal_text: str) -> ScoringInput:
        if not self.criteria:
            raise StateError("NO_CONFIRMED_CRITERIA")
        if not raw_proposal_text.strip():
            raise StateError("EMPTY_PROPOSAL")
        snapshot_analysis = deepcopy(self.analysis)
        snapshot_analysis.criterion_packets = deepcopy(self.packets)
        return ScoringInput(
            rfp_analysis=snapshot_analysis,
            raw_rfp_text=self.raw_rfp_text,
            raw_proposal_text=raw_proposal_text,
            confirmed_criteria=deepcopy(self.criteria),
        )
