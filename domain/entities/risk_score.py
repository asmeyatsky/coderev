"""
Risk Score Entity

Architectural Intent:
- Represents the AI-calculated risk score for a code review
- Encapsulates the various factors that contribute to the overall risk assessment
- Maintains invariants related to score calculation and validation
- Follows DDD principles with rich domain model

Key Design Decisions:
1. Risk scores are immutable after creation to maintain consistency of assessment
2. Multiple factors contribute to the overall score as defined in PRD section 2.4
3. Scores are normalized to a 0-100 range for consistency
4. Individual factor scores are preserved to enable detailed analysis
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class RiskScore:
    """
    RiskScore Domain Entity
    
    Invariants:
    - Overall score must be between 0 and 100
    - Individual factor scores must be between 0 and 100
    - Calculation timestamp must be present
    - Factor weights must be non-negative and sum to 1.0
    """
    
    id: str
    code_review_id: str
    calculated_at: datetime = field(default_factory=datetime.now)
    
    # Risk factors as defined in PRD section 2.4
    code_complexity_score: float = 0.0  # W_1: Cyclomatic complexity, etc.
    security_impact_score: float = 0.0  # W_2: Security vulnerabilities
    critical_files_score: float = 0.0   # W_3: Changes to high-risk files
    dataflow_confidence_score: float = 0.0  # W_4: Confidence in analysis
    test_coverage_delta_score: float = 0.0  # W_5: Changes in test coverage
    
    # Weights for each factor (should sum to 1.0)
    code_complexity_weight: float = 0.2
    security_impact_weight: float = 0.3
    critical_files_weight: float = 0.2
    dataflow_confidence_weight: float = 0.2
    test_coverage_delta_weight: float = 0.1
    
    # Additional metadata
    overall_score: Optional[float] = None
    risk_level: Optional[str] = None  # Low, Medium, High, Critical
    analysis_details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("RiskScore ID cannot be empty")
        if not self.code_review_id:
            raise ValueError("Code review ID cannot be empty")
        
        # Validate individual scores are within range
        for score_attr in [
            'code_complexity_score', 'security_impact_score', 'critical_files_score',
            'dataflow_confidence_score', 'test_coverage_delta_score'
        ]:
            score = getattr(self, score_attr)
            if not 0 <= score <= 100:
                raise ValueError(f"{score_attr} must be between 0 and 100, got {score}")
        
        # Validate weights sum to 1.0 (with small tolerance for floating point errors)
        total_weight = (
            self.code_complexity_weight +
            self.security_impact_weight +
            self.critical_files_weight +
            self.dataflow_confidence_weight +
            self.test_coverage_delta_weight
        )
        
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # Validate weights are non-negative
        for weight_attr in [
            'code_complexity_weight', 'security_impact_weight', 'critical_files_weight',
            'dataflow_confidence_weight', 'test_coverage_delta_weight'
        ]:
            weight = getattr(self, weight_attr)
            if weight < 0:
                raise ValueError(f"{weight_attr} must be non-negative, got {weight}")
        
        # Calculate overall score if not provided
        if self.overall_score is None:
            object.__setattr__(self, 'overall_score', self._calculate_overall_score())
        
        # Validate overall score is within range
        if self.overall_score is not None and not 0 <= self.overall_score <= 100:
            raise ValueError(f"Overall score must be between 0 and 100, got {self.overall_score}")
        
        # Set risk level if not provided
        if self.risk_level is None:
            object.__setattr__(self, 'risk_level', self._determine_risk_level(self.overall_score))
    
    def _calculate_overall_score(self) -> float:
        """Calculate the overall risk score based on weighted factors"""
        return (
            self.code_complexity_score * self.code_complexity_weight +
            self.security_impact_score * self.security_impact_weight +
            self.critical_files_score * self.critical_files_weight +
            self.dataflow_confidence_score * self.dataflow_confidence_weight +
            self.test_coverage_delta_score * self.test_coverage_delta_weight
        )
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on overall score"""
        if score < 20:
            return "Low"
        elif score < 40:
            return "Medium"
        elif score < 70:
            return "High"
        else:
            return "Critical"
    
    def update_factor_scores(
        self,
        code_complexity_score: Optional[float] = None,
        security_impact_score: Optional[float] = None,
        critical_files_score: Optional[float] = None,
        dataflow_confidence_score: Optional[float] = None,
        test_coverage_delta_score: Optional[float] = None
    ) -> 'RiskScore':
        """Update one or more factor scores and recalculate overall score"""
        new_code_complexity = code_complexity_score if code_complexity_score is not None else self.code_complexity_score
        new_security_impact = security_impact_score if security_impact_score is not None else self.security_impact_score
        new_critical_files = critical_files_score if critical_files_score is not None else self.critical_files_score
        new_dataflow_confidence = dataflow_confidence_score if dataflow_confidence_score is not None else self.dataflow_confidence_score
        new_test_coverage_delta = test_coverage_delta_score if test_coverage_delta_score is not None else self.test_coverage_delta_score
        
        # Validate the new scores
        for score, name in [
            (new_code_complexity, 'code_complexity_score'),
            (new_security_impact, 'security_impact_score'),
            (new_critical_files, 'critical_files_score'),
            (new_dataflow_confidence, 'dataflow_confidence_score'),
            (new_test_coverage_delta, 'test_coverage_delta_score')
        ]:
            if not 0 <= score <= 100:
                raise ValueError(f"{name} must be between 0 and 100, got {score}")
        
        new_overall_score = (
            new_code_complexity * self.code_complexity_weight +
            new_security_impact * self.security_impact_weight +
            new_critical_files * self.critical_files_weight +
            new_dataflow_confidence * self.dataflow_confidence_weight +
            new_test_coverage_delta * self.test_coverage_delta_weight
        )
        
        return RiskScore(
            id=self.id,
            code_review_id=self.code_review_id,
            calculated_at=datetime.now(),
            code_complexity_score=new_code_complexity,
            security_impact_score=new_security_impact,
            critical_files_score=new_critical_files,
            dataflow_confidence_score=new_dataflow_confidence,
            test_coverage_delta_score=new_test_coverage_delta,
            code_complexity_weight=self.code_complexity_weight,
            security_impact_weight=self.security_impact_weight,
            critical_files_weight=self.critical_files_weight,
            dataflow_confidence_weight=self.dataflow_confidence_weight,
            test_coverage_delta_weight=self.test_coverage_delta_weight,
            overall_score=new_overall_score,
            risk_level=self._determine_risk_level(new_overall_score),
            analysis_details=self.analysis_details
        )
    
    def needs_security_review(self) -> bool:
        """Determine if this risk score indicates a need for security review"""
        return self.security_impact_score > 50 or self.overall_score > 70
    
    def needs_qa_review(self) -> bool:
        """Determine if this risk score indicates a need for QA review"""
        return self.test_coverage_delta_score > 40 or self.overall_score > 60