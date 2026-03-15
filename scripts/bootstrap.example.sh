#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-stock-ai-workspace}"

mkdir -p "$PROJECT_ROOT"
cd "$PROJECT_ROOT"

git init

mkdir -p apps docs packages scripts

pnpm create next-app@latest apps/web \
  --ts --tailwind --eslint --app --use-pnpm --import-alias "@/*" --yes

pnpm add -C apps/web \
  ag-grid-community ag-grid-react @ag-grid-community/locale \
  @tanstack/react-query \
  zod react-hook-form @hookform/resolvers \
  next-themes \
  clsx class-variance-authority tailwind-merge lucide-react

(
  cd apps/web
  pnpm dlx shadcn@latest init -t next
)

mkdir -p apps/api/app
python -m venv .venv

cat > pnpm-workspace.yaml <<'EOF'
packages:
  - apps/*
  - packages/*
EOF

echo "초기 bootstrap 예시 완료"
echo "이후 AGENTS.md, docs/*, apps/api 기본 파일을 추가하세요."
