# MCT GitHub Actions Template

To use this template in a project:

1. Copy `mct.yml` to `.github/workflows/mct.yml`.
2. Copy `~/.claude/bin/mct` to `.github/mct/mct`.
3. Make `.github/mct/mct` executable.

This keeps CI behavior close to local `mct verify --mode pre-push`.
