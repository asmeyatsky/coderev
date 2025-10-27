"""
RiskScore Entity Tests

Test cases for the RiskScore domain entity.
Validating business rules, invariants, and behavior of the RiskScore entity.
"""

import pytest
from datetime import datetime
from ecrp.domain.entities.risk_score import RiskScore


class TestRiskScore:
    """Test cases for the RiskScore entity"""
    
    def test_risk_score_creation_with_valid_data(self):
        """Test creating a risk score with valid data"""
        # Act
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=30.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        
        # Assert
        assert risk_score.id == "risk-123"
        assert risk_score.code_review_id == "review-123"
        assert risk_score.code_complexity_score == 50.0
        assert risk_score.security_impact_score == 30.0
        assert risk_score.critical_files_score == 20.0
        assert risk_score.dataflow_confidence_score == 40.0
        assert risk_score.test_coverage_delta_score == 10.0
        assert risk_score.overall_score == pytest.approx(32.0)  # 50*.2 + 30*.3 + 20*.2 + 40*.2 + 10*.1
        assert risk_score.risk_level == "Low"
    
    def test_risk_score_creation_fails_with_invalid_score(self):
        """Test that risk score creation fails with invalid score"""
        # Act & Assert
        with pytest.raises(ValueError, match="code_complexity_score must be between 0 and 100"):
            RiskScore(
                id="risk-123",
                code_review_id="review-123",
                code_complexity_score=150.0,  # Invalid score > 100
                security_impact_score=30.0,
                critical_files_score=20.0,
                dataflow_confidence_score=40.0,
                test_coverage_delta_score=10.0
            )
    
    def test_risk_score_creation_fails_with_negative_score(self):
        """Test that risk score creation fails with negative score"""
        # Act & Assert
        with pytest.raises(ValueError, match="security_impact_score must be between 0 and 100"):
            RiskScore(
                id="risk-123",
                code_review_id="review-123",
                code_complexity_score=50.0,
                security_impact_score=-10.0,  # Invalid negative score
                critical_files_score=20.0,
                dataflow_confidence_score=40.0,
                test_coverage_delta_score=10.0
            )
    
    def test_risk_score_creation_fails_with_invalid_weights(self):
        """Test that risk score creation fails when weights don't sum to 1.0"""
        # Act & Assert
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            RiskScore(
                id="risk-123",
                code_review_id="review-123",
                code_complexity_score=50.0,
                security_impact_score=30.0,
                critical_files_score=20.0,
                dataflow_confidence_score=40.0,
                test_coverage_delta_score=10.0,
                code_complexity_weight=0.3,  # This would make total > 1.0
                security_impact_weight=0.3,
                critical_files_weight=0.2,
                dataflow_confidence_weight=0.2,
                test_coverage_delta_weight=0.1
            )
    
    def test_update_factor_scores_creates_new_instance(self):
        """Test that updating factor scores creates a new instance"""
        # Arrange
        original_risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=30.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        
        # Act
        updated_risk_score = original_risk_score.update_factor_scores(
            code_complexity_score=80.0,
            security_impact_score=70.0
        )
        
        # Assert
        assert original_risk_score.code_complexity_score == 50.0  # Original unchanged
        assert original_risk_score.security_impact_score == 30.0  # Original unchanged
        assert updated_risk_score.code_complexity_score == 80.0  # Updated value
        assert updated_risk_score.security_impact_score == 70.0  # Updated value
        assert original_risk_score is not updated_risk_score  # Different instances
        assert updated_risk_score.overall_score == pytest.approx(59.0)  # New overall score
    
    def test_needs_security_review_returns_true_for_high_security_score(self):
        """Test that needs_security_review returns True for high security score"""
        # Arrange
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=80.0,  # High security score
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        
        # Act
        needs_security_review = risk_score.needs_security_review()
        
        # Assert
        assert needs_security_review is True
    
    def test_needs_security_review_returns_true_for_high_overall_score(self):
        """Test that needs_security_review returns True for high overall score"""
        # Arrange
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=90.0,
            security_impact_score=20.0,
            critical_files_score=80.0,
            dataflow_confidence_score=60.0,
            test_coverage_delta_score=30.0
        )
        
        # Act
        needs_security_review = risk_score.needs_security_review()
        
        # Assert
        assert needs_security_review is True  # High overall score
    
    def test_needs_qa_review_returns_true_for_high_test_coverage_delta_score(self):
        """Test that needs_qa_review returns True for high test coverage delta score"""
        # Arrange
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=30.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=80.0  # High test coverage delta
        )
        
        # Act
        needs_qa_review = risk_score.needs_qa_review()
        
        # Assert
        assert needs_qa_review is True
    
    def test_risk_level_determination(self):
        """Test that risk level is determined correctly based on overall score"""
        # Test low risk
        low_risk = RiskScore(
            id="risk-low",
            code_review_id="review-123",
            code_complexity_score=10.0,
            security_impact_score=5.0,
            critical_files_score=5.0,
            dataflow_confidence_score=10.0,
            test_coverage_delta_score=5.0
        )
        assert low_risk.risk_level == "Low"
        
        # Test medium risk
        medium_risk = RiskScore(
            id="risk-medium",
            code_review_id="review-123",
            code_complexity_score=30.0,
            security_impact_score=25.0,
            critical_files_score=15.0,
            dataflow_confidence_score=20.0,
            test_coverage_delta_score=15.0
        )
        assert medium_risk.risk_level == "Medium"
        
        # Test high risk
        high_risk = RiskScore(
            id="risk-high",
            code_review_id="review-123",
            code_complexity_score=60.0,
            security_impact_score=55.0,
            critical_files_score=45.0,
            dataflow_confidence_score=50.0,
            test_coverage_delta_score=35.0
        )
        assert high_risk.risk_level == "High"
        
        # Test critical risk
        critical_risk = RiskScore(
            id="risk-critical",
            code_review_id="review-123",
            code_complexity_score=90.0,
            security_impact_score=85.0,
            critical_files_score=75.0,
            dataflow_confidence_score=80.0,
            test_coverage_delta_score=65.0
        )
        assert critical_risk.risk_level == "Critical"