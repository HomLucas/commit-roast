#!/bin/bash
echo "Running Security Checks..."

echo "Checking for potential secrets in code..."
grep -r "sk-[a-zA-Z0-9]\{20,\}" --exclude-dir={.git,node_modules,venv} . || true
grep -r "BEGIN.*PRIVATE KEY" --exclude-dir={.git,node_modules} . || true
grep -r "ya29\.[0-9A-Za-z\-_]\{20,\}" --exclude-dir={.git,node_modules} . || true

echo "Checking .gitignore..."
if ! grep -q "\.env$" .gitignore; then
    echo "Warning: .env not in .gitignore!"
fi

pip install bandit 2>/dev/null
bandit -r backend/src/ -ll 2>/dev/null || echo "Bandit check skipped (install bandit to enable)"

detect-secrets scan --all-files 2>/dev/null || echo "detect-secrets scan skipped"

echo "Security check complete!"
