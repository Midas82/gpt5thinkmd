import os, json, sys, fnmatch, hashlib, time
from pathlib import Path

cfg_path = Path.home().joinpath("refresh/organized/arch/geminicli/gpt5thinkmd/config.json")
out_dir  = Path.home().joinpath("refresh/index")
cfg = json.loads(cfg_path.read_text())
roots = [Path(os.path.expanduser(p)) for p in cfg.get("scan_roots", [])]
ignores = cfg.get("ignore_globs", [])
hash_mb = int(cfg.get("safety", {}).get("hash_large_files_over_mb", 50))
hash_threshold = hash_mb * 1024 * 1024

def ignored(p: Path):
    s = p.as_posix()
    return any(fnmatch.fnmatch(s, pat) for pat in ignores)

def sha256_file(p: Path):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

out_dir.mkdir(parents=True, exist_ok=True)
search = out_dir / "search.jsonl"
dupes  = out_dir / "dupes.csv"
large  = out_dir / "large.csv"
summary = out_dir / "summary.json"
cands = out_dir / "project_candidates.jsonl"

files_by_sig = {}   # (size, sha) -> [paths]
large_rows = []
total_files = 0
scanned_files = 0

with search.open("w", encoding="utf-8") as jout, \
     cands.open("w", encoding="utf-8") as jcand:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            d = Path(dirpath)
            # prune ignored dirs
            dirnames[:] = [dn for dn in dirnames if not ignored(d.joinpath(dn))]
            # simple project candidate heuristic
            markers = {"package.json","pyproject.toml","requirements.txt","Cargo.toml",".git","go.mod","Makefile","README.md"}
            if any((d / m).exists() for m in markers):
                jcand.write(json.dumps({"dir": d.as_posix(), "root": root.as_posix(), "markers": [m for m in markers if (d/m).exists()]})+"\n")
            for fn in filenames:
                p = d / fn
                if ignored(p):
                    continue
                try:
                    st = p.stat()
                except Exception:
                    continue
                total_files += 1
                rec = {
                    "path": p.as_posix(),
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                    "ext": p.suffix.lower()
                }
                sha = None
                if st.st_size >= hash_threshold:
                    try:
                        sha = sha256_file(p)
                    except Exception:
                        sha = None
                if sha:
                    rec["sha256"] = sha
                    files_by_sig.setdefault((st.st_size, sha), []).append(rec["path"])
                    large_rows.append((st.st_size, sha, rec["path"]))
                elif st.st_size >= hash_threshold:
                    large_rows.append((st.st_size, "", rec["path"]))
                jout.write(json.dumps(rec) + "\n")
                scanned_files += 1

# write dupes
with dupes.open("w", encoding="utf-8") as f:
    f.write("size,sha256,count,paths\n")
    for (sz, sha), paths in sorted(files_by_sig.items(), key=lambda x: (-len(x[1]), -x[0][0])):
        if len(paths) > 1:
            f.write(f"{sz},{sha},{len(paths)},\"{';'.join(paths)}\"\n")

# write large
with large.open("w", encoding="utf-8") as f:
    f.write("size,sha256,path\n")
    for sz, sha, path in sorted(large_rows, key=lambda x: -x[0]):
        f.write(f"{sz},{sha},{path}\n")

# summary
summary.write_text(json.dumps({
    "scanned_files": scanned_files,
    "total_files_seen": total_files,
    "hash_threshold_bytes": hash_threshold,
    "generated": int(time.time())
}, indent=2))