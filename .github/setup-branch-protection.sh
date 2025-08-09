#!/bin/bash

# GitHub Branch Protection Setup Script
# This script configures branch protection rules using GitHub CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed. Please install it first."
    print_error "Visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI. Please run 'gh auth login' first."
    exit 1
fi

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
print_status "Configuring branch protection for repository: $REPO"

# Function to set up branch protection
setup_branch_protection() {
    local branch=$1
    local required_reviews=$2
    local dismiss_stale=$3
    local require_code_owner=$4
    local required_checks=$5

    print_status "Setting up protection for branch: $branch"

    # Create the protection rule
    gh api \
        --method PUT \
        "/repos/$REPO/branches/$branch/protection" \
        --field required_status_checks="{\"strict\":true,\"checks\":[$required_checks]}" \
        --field enforce_admins=false \
        --field required_pull_request_reviews="{\"dismiss_stale_reviews\":$dismiss_stale,\"require_code_owner_reviews\":$require_code_owner,\"required_approving_review_count\":$required_reviews,\"require_last_push_approval\":true}" \
        --field restrictions=null \
        --field allow_force_pushes=false \
        --field allow_deletions=false \
        --field block_creations=false \
        --field required_conversation_resolution=true \
        --field lock_branch=false \
        --field allow_fork_syncing=false

    if [ $? -eq 0 ]; then
        print_status "✅ Branch protection configured successfully for $branch"
    else
        print_error "❌ Failed to configure branch protection for $branch"
        return 1
    fi
}

# Required status checks for main branch
main_checks='
{\"context\":\"Backend Tests\",\"app_id\":null},
{\"context\":\"Frontend Tests\",\"app_id\":null},
{\"context\":\"Security Scan\",\"app_id\":null},
{\"context\":\"Integration Suite\",\"app_id\":null}
'

# Required status checks for develop branch
develop_checks='
{\"context\":\"Backend Tests\",\"app_id\":null},
{\"context\":\"Frontend Tests\",\"app_id\":null},
{\"context\":\"Security Scan\",\"app_id\":null}
'

print_status "Configuring branch protection rules..."

# Configure main branch protection
print_status "Configuring main branch protection..."
setup_branch_protection "main" 2 true true "$main_checks"

# Configure develop branch protection
print_status "Configuring develop branch protection..."
setup_branch_protection "develop" 1 true false "$develop_checks"

# Create rulesets for additional protection (if available)
print_status "Creating additional repository rulesets..."

# Ruleset for all branches
cat > /tmp/ruleset.json << EOF
{
  "name": "Branch Protection Rules",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": ["~ALL"]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    }
  ]
}
EOF

# Apply the ruleset (if the API supports it)
gh api --method POST "/repos/$REPO/rulesets" --input /tmp/ruleset.json 2>/dev/null || {
    print_warning "Rulesets API not available or insufficient permissions. Skipping advanced rules."
}

# Clean up
rm -f /tmp/ruleset.json

print_status "Branch protection setup completed!"

# Verify the configuration
print_status "Verifying branch protection rules..."

echo ""
print_status "Main branch protection status:"
gh api "/repos/$REPO/branches/main/protection" --jq '{
  "required_reviews": .required_pull_request_reviews.required_approving_review_count,
  "dismiss_stale": .required_pull_request_reviews.dismiss_stale_reviews,
  "code_owner_required": .required_pull_request_reviews.require_code_owner_reviews,
  "status_checks": [.required_status_checks.checks[].context],
  "enforce_admins": .enforce_admins.enabled,
  "allow_force_pushes": .allow_force_pushes.enabled
}' 2>/dev/null || print_warning "Could not retrieve main branch protection details"

echo ""
print_status "Develop branch protection status:"
gh api "/repos/$REPO/branches/develop/protection" --jq '{
  "required_reviews": .required_pull_request_reviews.required_approving_review_count,
  "dismiss_stale": .required_pull_request_reviews.dismiss_stale_reviews,
  "code_owner_required": .required_pull_request_reviews.require_code_owner_reviews,
  "status_checks": [.required_status_checks.checks[].context],
  "enforce_admins": .enforce_admins.enabled,
  "allow_force_pushes": .allow_force_pushes.enabled
}' 2>/dev/null || print_warning "Could not retrieve develop branch protection details"

echo ""
print_status "🎉 Branch protection configuration complete!"
print_status ""
print_status "Next steps:"
print_status "1. Ensure all team members have appropriate repository permissions"
print_status "2. Configure required secrets in GitHub repository settings"
print_status "3. Test the CI/CD pipeline with a test pull request"
print_status "4. Set up notifications and monitoring integrations"
print_status ""
print_status "For more information, see .github/README.md"
