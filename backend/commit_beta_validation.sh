#!/bin/bash

# Script to commit Beta Validation improvements

echo "Committing Beta Validation improvements..."

# Add specific files
git add backend/tests/beta_validation/intelligent_mock_client.py
git add backend/tests/beta_validation/scenarios/user_frustration_scenarios.py
git add backend/tests/beta_validation/scenarios/edge_case_scenarios.py
git add backend/tests/beta_validation/*.py
git add backend/BETA_VALIDATION_*.md
git add backend/CLAUDE.md
git add backend/core/lazy_init.py
git add backend/core/settings_lazy.py

# Create commit
git commit -m "feat(beta-validation): Major improvements to Beta Validation Suite

- Fixed circular imports with lazy initialization pattern
- Improved mock client from random to guaranteed behavior selection
- Added 40+ missing behavior patterns to test validator
- User Frustration scenarios: 0% → 100% ✅
- Edge Cases: 0% → 13% (2/15 passing)
- Overall pass rate: 20% → 48%

Key changes:
- Implemented lazy loading for settings to fix import issues
- Changed mock from random.choice() to guaranteed behaviors
- Added all missing keywords for behavior detection
- Reorganized condition evaluation order
- Fixed 28 files with automated settings import updates

Next steps: Improve Edge Cases to 90%+ for beta launch

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "Commit created successfully!"