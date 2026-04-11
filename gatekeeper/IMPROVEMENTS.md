# Improvements To Do

- [ ] We are creating and deleting a new docker container on every run, and reinstalling dependencies. We can find a way to reuse the same one
- [ ] More user configuration
- [ ] Output format is messy
- [ ] Installation is always repo-wide (.pre-commit-config is commited) - investigate if local only option is possible
- [ ] Precommit hook currently scans whole repo, while commonly it should only be changed files (or changed diffs)
- [ ] Parse the whole findings (result of the scan)
- [ ] Add python policy engine