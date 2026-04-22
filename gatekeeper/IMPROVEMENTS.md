# Improvements To Do

- [ ] More user configuration
- [ ] Precommit hook currently scans whole repo, while commonly it should only be changed files (or changed diffs). Maybe an option?
- [ ] Find way to parse the whole findings (result of the scan). Preferably in tools-config.yaml? I assume parsing is important here because of next point
- [ ] Add python policy engine and add checks to fail the precommit
- [ ] Pick and implement one extension: HTML Dashboard, Waiver system, CI/CD integration, LLM explanation