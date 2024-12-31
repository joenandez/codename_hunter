# Release v{VERSION}

## Pre-release Checklist
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with all changes
- [ ] All tests passing on main branch
- [ ] Documentation updated to reflect changes
- [ ] Release notes drafted using RELEASE_TEMPLATE.md
- [ ] All dependencies up to date
- [ ] No outstanding critical issues

## Release Process Checklist
- [ ] Create and push version tag (`vX.Y.Z`)
- [ ] Monitor GitHub Actions workflow
- [ ] Verify TestPyPI deployment
- [ ] Test installation from TestPyPI
- [ ] Verify PyPI deployment
- [ ] Test installation from PyPI
- [ ] Verify GitHub release created

## Post-release Checklist
- [ ] Announce release (if applicable)
- [ ] Update documentation website (if applicable)
- [ ] Close related issues
- [ ] Update project board

## Notes
Add any additional notes or context about this release.

## Related Issues
- Closes #issue_number
- Addresses #issue_number 