## Deploy Configuration (configured by /setup-deploy)
- Platform: Vercel
- Production URL: https://muletownlaw-legal-docs.vercel.app
- Deploy workflow: auto-deploy on push to main (via GitHub integration)
- Deploy status command: HTTP health check
- Merge method: merge
- Project type: web app (static HTML)
- Post-deploy health check: https://muletownlaw-legal-docs.vercel.app

### Custom deploy hooks
- Pre-merge: none
- Deploy trigger: automatic on push to main
- Deploy status: poll production URL
- Health check: https://muletownlaw-legal-docs.vercel.app

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
