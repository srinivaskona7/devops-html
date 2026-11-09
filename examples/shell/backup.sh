#!/usr/bin/env bash
# backup.sh - archive a directory, keep the newest N archives, never run twice at once.
set -Eeuo pipefail
IFS=$'\n\t'

readonly PROG="${0##*/}"
readonly LOCK_DIR="${TMPDIR:-/tmp}/${PROG}.lock"

usage() {
  cat <<USAGE
Usage: ${PROG} [-n] [-k KEEP] [-v] SOURCE DEST
  -n        dry run: show what would happen
  -k KEEP   archives to keep (default 7)
  -v        verbose
USAGE
}

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*" >&2; }
die() {
  log "ERROR: $*"
  exit "${2:-1}"
}

have_lock=0
cleanup() {
  local rc=$?
  # only the run that created the lock may remove it
  ((have_lock)) && rmdir "${LOCK_DIR}" 2>/dev/null || true
  [[ -n ${TMP_ARCHIVE:-} && -f ${TMP_ARCHIVE} ]] && rm -f -- "${TMP_ARCHIVE}"
  ((rc == 0)) || log "failed with exit code ${rc}"
  exit "${rc}"
}
trap cleanup EXIT
trap 'die "interrupted" 130' INT TERM

dry_run=0 keep=7 verbose=0
while getopts ':nk:vh' opt; do
  case ${opt} in
    n) dry_run=1 ;;
    k) keep=${OPTARG} ;;
    v) verbose=1 ;;
    h)
      usage
      exit 0
      ;;
    :)
      usage >&2
      die "option -${OPTARG} needs a value" 2
      ;;
    *)
      usage >&2
      die "unknown option -${OPTARG}" 2
      ;;
  esac
done
shift $((OPTIND - 1))

(($# == 2)) || {
  usage >&2
  die "need SOURCE and DEST" 2
}
[[ ${keep} =~ ^[0-9]+$ ]] || die "KEEP must be a number, got '${keep}'" 2
src=$1 dest=$2
[[ -d ${src} ]] || die "source not found: ${src}"
mkdir -p -- "${dest}"

mkdir -- "${LOCK_DIR}" 2>/dev/null || die "another run is in progress (${LOCK_DIR})" 3
have_lock=1

stamp=$(date -u +%Y%m%dT%H%M%SZ)
archive="${dest}/$(basename -- "${src}")-${stamp}.tar.gz"
TMP_ARCHIVE="${archive}.partial"

((verbose)) && log "archiving ${src} -> ${archive}"
if ((dry_run)); then
  log "dry run: would create ${archive}"
else
  tar -czf "${TMP_ARCHIVE}" -C "$(dirname -- "${src}")" "$(basename -- "${src}")"
  mv -- "${TMP_ARCHIVE}" "${archive}"
  TMP_ARCHIVE=
  log "created ${archive}"
fi

mapfile -t old < <(find "${dest}" -maxdepth 1 -name '*.tar.gz' -print | sort -r | tail -n +"$((keep + 1))")
for f in "${old[@]}"; do
  [[ -n ${f} ]] || continue
  if ((dry_run)); then log "dry run: would delete ${f}"; else
    rm -f -- "${f}"
    log "pruned ${f}"
  fi
done
