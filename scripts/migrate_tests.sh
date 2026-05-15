#!/usr/bin/env bash
# scripts/migrate_tests.sh
#
# Reorganises the API test suite from monolithic files into focused,
# per-HTTP-method modules under tests/api/v1/.
#
# Run from anywhere inside the serve repo:
#   bash backend/scripts/migrate_tests.sh
#
# The script is idempotent: it won't overwrite files that already exist.
# After running, verify with:  cd backend && pytest tests/ -q

set -euo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)/backend"
NEW_ROOT="$REPO_ROOT/tests/api/v1"

# ── 1. Create directory structure ─────────────────────────────────────────────
mkdir -p "$NEW_ROOT"/{transactions,summary,accounts,households,labels,auth}

# ── 2. Verify all scaffold files are present ──────────────────────────────────
MISSING=0
for f in \
  conftest.py \
  transactions/__init__.py \
  transactions/conftest.py \
  transactions/test_get.py \
  transactions/test_post.py \
  transactions/test_patch.py \
  transactions/test_delete.py \
  transactions/test_import.py \
  summary/__init__.py \
  summary/conftest.py \
  summary/test_get.py \
  accounts/__init__.py \
  accounts/conftest.py \
  accounts/test_get.py \
  accounts/test_post.py \
  accounts/test_patch.py \
  accounts/test_delete.py \
  households/__init__.py \
  households/conftest.py \
  households/test_get.py \
  households/test_post.py \
  households/test_patch.py \
  households/test_delete.py \
  households/test_members.py \
  labels/__init__.py \
  labels/conftest.py \
  labels/test_get.py \
  labels/test_post.py \
  labels/test_patch.py \
  labels/test_delete.py \
  auth/__init__.py \
  auth/conftest.py \
  auth/test_register.py \
  auth/test_login.py \
  auth/test_logout.py \
  auth/test_me.py
do
  target="$NEW_ROOT/$f"
  if [[ ! -f "$target" ]]; then
    echo "Missing scaffold file: $target"
    MISSING=1
  fi
done

if [[ $MISSING -eq 1 ]]; then
  echo "Place the scaffold files first, then re-run this script."
  exit 1
fi

echo "✓ All scaffold files present"

# ── 3. Remove old monolithic files ────────────────────────────────────────────
for old_file in \
  test_transactions.py \
  test_pagination.py \
  test_summary.py \
  test_accounts.py \
  test_households.py \
  test_labels.py \
  test_auth.py
do
  path="$NEW_ROOT/$old_file"
  if [[ -f "$path" ]]; then
    rm "$path"
    echo "✓ Removed $old_file"
  else
    echo "  (already removed) $old_file"
  fi
done

# ── 4. Run the full test suite ────────────────────────────────────────────────
echo ""
echo "Running tests…"
cd "$REPO_ROOT"
python -m pytest tests/ -q --tb=short
