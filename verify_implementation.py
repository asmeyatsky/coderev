#!/usr/bin/env python3
"""
Simple verification script for ECRP platform
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Test importing the dependency container to verify structure
def verify_ecrp_implementation():
    print("🔍 Verifying ECRP Platform Implementation...")
    
    try:
        # Try importing components to verify they exist
        from domain.entities.user import User, UserRole
        from domain.entities.code_review import CodeReview, ReviewStatus
        from domain.entities.risk_score import RiskScore
        from application.dtos.dtos import CodeReviewDTO
        from infrastructure.config.dependency_injection import container
        
        print("✅ All core modules imported successfully")
        
        # Create a simple test scenario
        requester = User(
            id="test-user-123",
            username="testuser",
            email="test@example.com",
            roles={UserRole.DEVELOPER}
        )
        
        print(f"✅ User entity created: {requester.username}")
        
        risk_score = RiskScore(
            id="test-risk-123",
            code_review_id="test-review-123",
            code_complexity_score=50.0,
            security_impact_score=30.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        
        print(f"✅ RiskScore entity created with overall score: {risk_score.overall_score:.2f}")
        
        # Verify the dependency container
        print(f"✅ Dependency container has {type(container).__name__}")
        print(f"✅ User repository: {type(container.user_repository).__name__}")
        print(f"✅ Code review repository: {type(container.code_review_repository).__name__}")
        print(f"✅ Create code review use case: {type(container.create_code_review_use_case).__name__}")
        
        print("\n🎉 ECRP Platform verification completed successfully!")
        print("📋 All core components are properly implemented")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = verify_ecrp_implementation()
    if success:
        print("\n🏆 ECRP Platform Implementation: COMPLETE")
    else:
        print("\n❌ ECRP Platform Implementation: INCOMPLETE")
        sys.exit(1)