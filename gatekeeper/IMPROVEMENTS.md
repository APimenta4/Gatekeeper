# Improvements To Do

- [ ] More user configuration
- [ ] Add more SAST tools. The README.md describes a few, but most are not implemented yet
- [ ] Precommit hook currently scans whole repo, while commonly it should only be changed files (or changed diffs). Maybe an option?
- [ ] Kind of related to the previous point, but we are currently scanning things like .venv, .node_modules, dist, build, etc... If we cannot implement the previous point, we should at least find a way to circumvent this
- [ ] Find way to parse the whole findings (result of the scan). Preferably in tools-config.yaml? I assume parsing is important here because of next point
- [ ] Add python policy engine and add checks to fail the precommit
- [ ] Pick and implement one extension: HTML Dashboard, Waiver system, CI/CD integration, LLM explanation