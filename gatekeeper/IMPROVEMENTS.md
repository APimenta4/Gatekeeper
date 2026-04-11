# Improvements To Do

- [ ] We are creating and deleting a new docker container on every run, and reinstalling dependencies. We can find a way to reuse the same one
- [ ] More user configuration
- [ ] Precommit hook currently scans whole repo, while commonly it should only be changed files (or changed diffs)
- [ ] Parse the whole findings (result of the scan)
- [ ] Add python policy engine and add checks to fail the precommit