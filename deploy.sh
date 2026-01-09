
# Deploy script for wireguard-manager
# Syncs the project to remote server using rsync

set -e

REMOTE_USER="sudip"
REMOTE_HOST="test"
REMOTE_PATH="wireguard-manager"
LOCAL_PATH="$(cd "$(dirname "$0")" && pwd)"

echo "Deploying wireguard-manager to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"

# Rsync options:
# -a: archive mode (preserves permissions, timestamps, etc.)
# -v: verbose
# -z: compress during transfer
# --delete: delete files on remote that don't exist locally
# --exclude: exclude certain files/directories
set -vx
rsync -ravz --delete \
  --exclude '.git/' \
  --exclude '.pytest_cache/' \
  --exclude 'venv/' \
  --exclude 'out' \
  --exclude 'node_modules/' \
  --exclude '.next/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  --exclude '.vscode/' \
  "${LOCAL_PATH}/" \
  "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"

echo "Deployment complete!"
