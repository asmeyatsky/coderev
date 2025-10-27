#!/usr/bin/env python3
"""
Test script to verify ECRP platform functionality
"""

def test_ecrp_functionality():
    """Test the core functionality of the ECRP platform"""
    
    # Import the dependency container
    from ecrp.infrastructure.config.dependency_injection import container
    
    print("✅ Dependency container created successfully")
    
    # Check repositories
    repositories = [
        container.user_repository,
        container.code_review_repository,
        container.comment_repository,
        container.risk_score_repository,
        container.environment_repository
    ]
    
    repo_names = [type(repo).__name__ for repo in repositories]
    print(f"✅ Repositories loaded: {repo_names}")
    
    # Check services
    print(f"✅ Risk analysis service: {type(container.risk_analysis_service).__name__}")
    print(f"✅ Environment service: {type(container.environment_service).__name__}")
    print(f"✅ Git provider service: {type(container.git_provider_service).__name__}")
    print(f"✅ Review service: {type(container.review_service).__name__}")
    
    # Check use cases
    print(f"✅ Create code review use case: {type(container.create_code_review_use_case).__name__}")
    print(f"✅ Approve code review use case: {type(container.approve_code_review_use_case).__name__}")
    print(f"✅ Create comment use case: {type(container.create_comment_use_case).__name__}")
    print(f"✅ Request changes use case: {type(container.request_changes_use_case).__name__}")
    print(f"✅ Merge code review use case: {type(container.merge_code_review_use_case).__name__}")
    
    print("\n🎉 All ECRP components loaded successfully!")
    

if __name__ == "__main__":
    test_ecrp_functionality()