#!/usr/bin/env bats

setup() {
  SRC="$BATS_TEST_TMPDIR/data"
  DEST="$BATS_TEST_TMPDIR/backups"
  mkdir -p "$SRC"
  echo hello > "$SRC/a.txt"
  export TMPDIR="$BATS_TEST_TMPDIR"        # lock directory lives in the test's own temp dir
}

@test "creates a compressed archive" {
  run ./backup.sh "$SRC" "$DEST"
  [ "$status" -eq 0 ]
  [ "$(find "$DEST" -name '*.tar.gz' | wc -l)" -eq 1 ]
}

@test "archive contains the source files" {
  ./backup.sh "$SRC" "$DEST"
  run tar -tzf "$(find "$DEST" -name '*.tar.gz')"
  [[ "$output" == *"data/a.txt"* ]]
}

@test "dry run changes nothing" {
  run ./backup.sh -n "$SRC" "$DEST"
  [ "$status" -eq 0 ]
  [[ "$output" == *"dry run: would create"* ]]
  [ "$(find "$DEST" -name '*.tar.gz' | wc -l)" -eq 0 ]
}

@test "keeps only the newest N archives" {
  for i in 1 2 3; do ./backup.sh -k 2 "$SRC" "$DEST"; sleep 1; done
  [ "$(find "$DEST" -name '*.tar.gz' | wc -l)" -eq 2 ]
}

@test "missing arguments is a usage error (exit 2)" {
  run ./backup.sh
  [ "$status" -eq 2 ]
  [[ "$output" == *"need SOURCE and DEST"* ]]
}

@test "non-numeric -k is rejected (exit 2)" {
  run ./backup.sh -k abc "$SRC" "$DEST"
  [ "$status" -eq 2 ]
}

@test "unknown source fails with exit 1" {
  run ./backup.sh "$BATS_TEST_TMPDIR/nope" "$DEST"
  [ "$status" -eq 1 ]
}

@test "refuses to run while another run holds the lock (exit 3)" {
  mkdir "$BATS_TEST_TMPDIR/backup.sh.lock"
  run ./backup.sh "$SRC" "$DEST"
  [ "$status" -eq 3 ]
  [ -d "$BATS_TEST_TMPDIR/backup.sh.lock" ]      # and does not steal or delete it
}

@test "releases the lock when finished" {
  ./backup.sh "$SRC" "$DEST"
  [ ! -d "$BATS_TEST_TMPDIR/backup.sh.lock" ]
}
