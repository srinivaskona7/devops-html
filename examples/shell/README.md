# backup.sh — the script built in the Shell Scripting video

Tested with bash 5.2, ShellCheck 0.11, shfmt 3.14 and Bats 1.14 (9 of 9 tests pass).
macOS ships bash 3.2, which lacks `mapfile`; install bash 4+ (`brew install bash`) or run on Linux.

```bash
./backup.sh -v data backups          # archive, keep 7
./backup.sh -n -k 3 data backups     # dry run, keep 3
bats tests/backup.bats               # run the tests
shellcheck backup.sh && shfmt -d -i 2 -ci backup.sh
```
Exit codes: 0 ok, 1 error, 2 usage error, 3 another run holds the lock.
