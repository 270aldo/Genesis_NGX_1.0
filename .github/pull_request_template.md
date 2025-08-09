# Pull Request

## Description

Brief description of what this PR does and why it's needed.

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Configuration change
- [ ] 🎨 Code style/formatting
- [ ] ♻️ Code refactoring
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security fix
- [ ] 🧪 Test additions or modifications

## Related Issues

Fixes #(issue number)

## Changes Made

-
-
-

## Testing

### Backend Testing

- [ ] Unit tests pass locally
- [ ] Integration tests pass locally
- [ ] Agent tests pass (if applicable)
- [ ] Beta validation tests pass (if applicable)
- [ ] Manual testing completed

### Frontend Testing

- [ ] Component tests pass
- [ ] Integration tests pass
- [ ] Manual UI testing completed
- [ ] Cross-browser testing (if applicable)
- [ ] Mobile responsive testing (if applicable)

## Quality Assurance

### Code Quality

- [ ] Code follows project conventions
- [ ] Linting passes (ruff for backend, ESLint for frontend)
- [ ] Type checking passes (mypy for backend, TypeScript for frontend)
- [ ] Code is documented (docstrings, comments where needed)

### Security

- [ ] No secrets or sensitive data in code
- [ ] Security implications considered and addressed
- [ ] Authentication/authorization properly implemented (if applicable)
- [ ] Input validation implemented (if applicable)

### Performance

- [ ] Performance impact considered
- [ ] No unnecessary database queries
- [ ] Caching implemented where appropriate
- [ ] Bundle size impact minimal (frontend changes)

## Dependencies

### Backend

- [ ] No new dependencies added, or dependencies are justified
- [ ] Poetry lock file updated
- [ ] Requirements are pinned to compatible versions

### Frontend

- [ ] No new dependencies added, or dependencies are justified
- [ ] Package-lock.json updated
- [ ] Dependencies are compatible with existing versions

## Deployment Considerations

- [ ] Database migrations included (if applicable)
- [ ] Environment variables documented (if applicable)
- [ ] Configuration changes documented
- [ ] Rollback plan considered
- [ ] Health check endpoints working

## Documentation

- [ ] Code changes are self-documenting or commented
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] User documentation updated (if applicable)

## Screenshots/Videos (if applicable)
<!-- Add screenshots or videos to demonstrate UI changes -->

## Additional Notes
<!-- Any additional information, concerns, or decisions that reviewers should know about -->

## Checklist for Reviewers

- [ ] Code review completed
- [ ] Tests are adequate and pass
- [ ] Security implications reviewed
- [ ] Performance impact acceptable
- [ ] Documentation is sufficient
- [ ] Changes align with project architecture

---

## Conventional Commits

This PR follows [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **Format**: `type(scope): description`
- **Example**: `feat(agents): add new nutrition analysis capabilities`

**Commit Types**: feat, fix, docs, style, refactor, perf, test, build, ci, chore
