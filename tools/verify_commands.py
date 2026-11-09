#!/usr/bin/env python3
"""Verify every CLI command shown in the videos against the real, installed tools.

For each `$ tool subcommand --flag ...` line in content/*.js it checks that
  1. the subcommand exists (tool help succeeds for it), and
  2. every --flag used appears in that subcommand's help text.
Nothing is executed against any cloud: only `--help` pages are read.

    python3 tools/verify_commands.py                 # all tools, all videos
    python3 tools/verify_commands.py --tools aws gcloud --videos aws gcp
    python3 tools/verify_commands.py --fail          # exit 1 on any problem (CI)

Results are cached in .cache/verify-cache.json (delete it after upgrading a CLI).
"""
import argparse, json, os, pathlib, re, shlex, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

CACHE_F = ROOT / ".cache" / "verify-cache.json"
ENV = dict(os.environ)
ENV["PATH"] = ":".join([str(pathlib.Path.home() / "bin"), "/opt/homebrew/bin", "/usr/local/bin",
                        "/Applications/Docker.app/Contents/Resources/bin", ENV.get("PATH", "")])
_pl = pathlib.Path("/tmp/dockercfg/cli-plugins")
if not _pl.exists():
    os.makedirs("/tmp/dockercfg", exist_ok=True)
    try:
        _pl.symlink_to("/Applications/Docker.app/Contents/Resources/cli-plugins")
    except OSError:
        pass
ENV.update(AWS_PAGER="", PAGER="cat", CLOUDSDK_CONFIG="/tmp/gcloudcfg", DOCKER_CONFIG="/tmp/dockercfg", NO_COLOR="1",
           CLOUDSDK_CORE_DISABLE_PROMPTS="1", TERM="dumb")
os.makedirs("/tmp/gcloudcfg", exist_ok=True); os.makedirs("/tmp/dockercfg", exist_ok=True)

GLOBAL = {  # flags accepted everywhere by the tool, not always listed on each page
    "aws": {"--region", "--output", "--query", "--profile", "--debug", "--no-cli-pager", "--cli-input-json", "--endpoint-url",
            "--generate-cli-skeleton", "--no-paginate", "--no-verify-ssl", "--ca-bundle", "--color", "--no-sign-request", "--version"},
    "gcloud": {"--project", "--format", "--quiet", "--verbosity", "--impersonate-service-account", "--help", "--filter", "--limit",
               "--sort-by", "--flatten", "--page-size", "--uri", "--billing-project", "--account", "--log-http", "--configuration"},
    "kubectl": {"--namespace", "--context", "--kubeconfig", "--as", "--as-group", "--server", "--token", "--request-timeout", "--v", "--help"},
    "helm": {"--namespace", "--kube-context", "--kubeconfig", "--debug", "--help"},
    "docker": {"--help", "--version", "--context", "--host", "--config", "--net"},
    "terraform": {"-policies"},  # accepted by plan/apply/query in 1.17 (not listed on every help page)
}


def load_cache():
    return json.loads(CACHE_F.read_text()) if CACHE_F.exists() else {}


CACHE = load_cache()


def help_text(tool, path):
    """Return help text for `tool path...`, or None if that command does not exist."""
    key = tool + " " + " ".join(path)
    if key in CACHE:
        return CACHE[key]
    if tool == "aws":
        cmd = ["aws", *path, "help"]
    elif tool == "terraform":
        cmd = ["terraform", *path, "-help"]
    else:
        cmd = [tool, *path, "--help"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=ENV, stdin=subprocess.DEVNULL)
        out = r.stdout + "\n" + r.stderr
        if tool == "aws":
            out = subprocess.run(["col", "-b"], input=out, capture_output=True, text=True).stdout
        bad = ("invalid choice" in out.lower() or "unknown command" in out.lower() or "unknown help topic" in out.lower()
               or "invalid command" in out.lower() or "usage: aws" in out.lower() and "invalid" in out.lower()
               or "not recognized" in out.lower() or "did you mean" in out.lower() and r.returncode != 0
               or "failed to load" in out.lower() or "usage: terraform" in out.lower() and r.returncode != 0 and len(out) < 400)
        res = None if (r.returncode != 0 and not out.strip()) or bad else out
    except Exception:
        res = None
    CACHE[key] = res
    CACHE_F.parent.mkdir(exist_ok=True); CACHE_F.write_text(json.dumps(CACHE))  # save progress after every lookup
    return res


def commands_in(scene):
    """Yield joined command strings that start with '$ '."""
    cur = None
    for line in scene.get("cmd", []) or []:
        s = str(line)
        if s.startswith("$ "):
            if cur: yield cur
            cur = s[2:].rstrip()
        elif cur is not None and cur.endswith("\\"):
            cur = cur[:-1].rstrip() + " " + s.strip()
        else:
            if cur: yield cur
            cur = None
    if cur: yield cur


def tokens(cmdline):
    cmdline = re.sub(r"\s#.*$", "", cmdline)  # trailing comment
    try:
        lex = shlex.shlex(cmdline, posix=True, punctuation_chars="|&;<>")
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        toks = cmdline.split()
    out = []
    for t in toks:
        if t and t[0] in "|&;<>":
            break  # pipeline / redirect: only inspect the first command
        if t == "--" and out:
            break  # everything after a bare "--" is the inner command's own arguments
        out.append(t)
    return out


def check_command(tool, toks):
    """Return (status, detail). status in ok | bad-command | bad-flag | skip."""
    rest = toks[1:]
    path = []
    for t in rest[:6]:
        if t.startswith("-") or "=" in t or t.startswith(("$", "<", "(", "{", "[", "/", ".", "~", "'", '"')) or t.isdigit():
            break
        if tool == "aws" and len(path) >= 3:
            break
        if "/" in t or ":" in t or "." in t:
            break  # a URI, ARN, file name or similar: an argument, never a subcommand
        path.append(t)
    if not path:
        return "skip", "no subcommand"
    # longest valid prefix
    best, text = None, None
    for n in range(1, len(path) + 1):
        h = help_text(tool, path[:n])
        if h is None:
            break
        best, text = path[:n], h
    if best is None:
        return "bad-command", " ".join(path[:2])
    if tool in ("aws",) and len(best) < 2:
        return "bad-command", " ".join(path[:2])
    flags = []
    for t in rest:
        if tool == "terraform":
            if re.match(r"^-[a-z][a-z0-9-]*", t) and not t.startswith("--"):
                flags.append(re.match(r"^(-[a-z][a-z0-9-]*)", t).group(1))
        elif t.startswith("--") and len(t) > 2:
            if tool == "docker" and "." in t.split("=")[0]:
                continue  # e.g. --path.rootfs: an argument to the image's program, not to docker
            flags.append(t.split("=")[0])
    missing = []
    for f in flags:
        if f in GLOBAL.get(tool, set()):
            continue
        base = f.replace("--no-", "--", 1) if f.startswith("--no-") else f
        if re.search(re.escape(f) + r"(?![a-z0-9-])", text) or re.search(re.escape(base) + r"(?![a-z0-9-])", text):
            continue
        missing.append(f)
    if missing:
        return "bad-flag", f"{' '.join(best)}: {' '.join(missing)}"
    return "ok", " ".join(best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools", nargs="*", default=["aws", "gcloud", "kubectl", "helm", "terraform", "docker"])
    ap.add_argument("--videos", nargs="*")
    ap.add_argument("--fail", action="store_true")
    a = ap.parse_args()
    stats, problems = {}, []
    for f in sorted((ROOT / "content").glob("*.js")):
        vid = f.stem
        if a.videos and vid not in a.videos:
            continue
        d = build.load(f)
        for i, s in enumerate(d["scenes"], 1):
            for c in commands_in(s):
                toks = tokens(c)
                if not toks or toks[0] not in a.tools:
                    continue
                tool = toks[0]
                st, det = check_command(tool, toks)
                stats.setdefault(tool, {}).setdefault(st, 0)
                stats[tool][st] += 1
                if st in ("bad-command", "bad-flag"):
                    problems.append((tool, vid, i, s.get("title", ""), st, det, c[:110]))
        CACHE_F.parent.mkdir(exist_ok=True); CACHE_F.write_text(json.dumps(CACHE))
    print(f"{'tool':<10}{'ok':>6}{'bad cmd':>9}{'bad flag':>10}{'skipped':>9}")
    for t, d in stats.items():
        print(f"{t:<10}{d.get('ok', 0):>6}{d.get('bad-command', 0):>9}{d.get('bad-flag', 0):>10}{d.get('skip', 0):>9}")
    for p in problems:
        print(f"\n[{p[0]}] {p[1]} scene {p[2]} '{p[3]}': {p[4]} -> {p[5]}\n    {p[6]}")
    if a.fail and problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
