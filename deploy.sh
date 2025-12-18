set -e

echo "Starting deployment..."

if [ ! -f "credentials.json" ]; then
  echo "credentials.json not found at repository root"
  exit 1
fi

if [ ! -f "requirements.txt" ]; then
  echo "requirements.txt not found at repository root"
  exit 1
fi

if [ ! -f ".env" ]; then
  echo ".env not found at repository root"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment (.venv)"
  python3 -m venv .venv
else
  echo "Virtual environment already exists"
fi

source .venv/bin/activate

echo "Installing dependencies..."

if command -v uv >/dev/null 2>&1; then
  echo "Using uv for fast installs"
  uv pip install --system -r requirements.txt
else
  echo "Using pip"
  pip install --upgrade pip
  pip install -r requirements.txt
fi

echo "Starting FastAPI server on port 8080..."

nohup .venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8080 \
  --log-level info \
  > server.log 2>&1 &

sleep 3

echo "Deployment complete"
echo "Server running at http://0.0.0.0:8080"
