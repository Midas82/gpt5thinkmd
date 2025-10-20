#!/usr/bin/env bash
# scripts/gen_task_stubs.sh /path/to/workspace
set -euo pipefail
ws="$1"; rup="$ws/docs/README.upstream.md"; tasks="$ws/ops/tasks"
mkdir -p "$tasks"
awk '
  BEGIN{inblk=0}
  /^```[[:alnum:]]*/{inblk = !inblk; if(!inblk){print "__BLOCK_END__"}; next}
  { if(inblk){ print } }
' "$rup" \
| awk 'BEGIN{n=0}{ if($0=="__BLOCK_END__"){ n++ } else { print > "/tmp/_tb" n ".sh" } } END{ print n > "/tmp/_tb_count" }'

count=$(cat /tmp/_tb_count 2>/dev/null || echo 0)
pad() { printf "%02d" "$1"; }
for i in $(seq 0 "${count:-0}"); do
  src="/tmp/_tb${i}.sh"; [[ -s "$src" ]] || continue
  tgt="$tasks/$(pad "$i")-block.sh"
  {
    echo '#!/usr/bin/env bash'
    echo 'set -euo pipefail'
    sed -E 's/^\$[[:space:]]+//; s/\r$//' "$src"
  } > "$tgt"
  chmod +x "$tgt"
  echo "stub: $tgt"
done
rm -f /tmp/_tb*.sh /tmp/_tb_count
