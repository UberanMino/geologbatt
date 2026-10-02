#!/usr/bin/env bash
# Shows whether the current branch is based on the latest overall state:
# - which remote branches contain work that is NOT yet in the default branch
# - which files those branches change
# - whether the current branch is behind the default branch
# Run at the start of every session (see CLAUDE.md).
set -euo pipefail
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*' 2>/dev/null || git fetch -q origin
DEFAULT=$(git remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p')
D="origin/${DEFAULT}"
CUR=$(git rev-parse --abbrev-ref HEAD)
echo "Default branch: ${DEFAULT} ($(git log -1 --format='%h %ci' "$D"))"
echo "Current branch: ${CUR}"
behind=$(git rev-list --count "HEAD..$D")
if [ "$behind" -gt 0 ]; then
  echo "!! Current branch is ${behind} commit(s) behind the default branch -> run 'git merge $D' first"
else
  echo "OK: current branch contains the default branch"
fi
echo
found=0
for b in $(git branch -r | grep -v HEAD | sed 's/^ *//'); do
  [ "$b" = "$D" ] && continue
  ahead=$(git rev-list --count "$D..$b")
  [ "$ahead" -eq 0 ] && continue
  if git merge-base --is-ancestor "$b" HEAD; then continue; fi
  found=1
  mb=$(git merge-base "$D" "$b")
  echo "!! $b: ${ahead} commit(s) not in the default branch (last: $(git log -1 --format='%ci %s' "$b" | cut -c1-80))"
  git diff --name-only "$mb" "$b" | grep -v '\.xlsx$\|\.pdf$\|\.woff2$\|\.jpg$\|\.png$' | sed 's/^/      /' | head -15
done
[ "$found" -eq 0 ] && echo "OK: no unmerged branches – the current branch has the latest state."
exit 0
