executer = """
#!/bin/bash

echo -e ' ▄▀▀ █▄█ ▄▀▄ ▄▀▀ ▄▀▄ █   ▄▀▄ ▀█▀ ██▀
 ▀▄▄ █ █ ▀▄▀ ▀▄▄ ▀▄▀ █▄▄ █▀█  █  █▄▄'

echo '------------------------------------------'

set -e  # Exit on error

# 1) Check if python is installed
if ! python3 --version >/dev/null 2>&1; then
    echo "❌ Python3 is not installed. Install it and try again."
    exit 1
fi

# 2) Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# 3) Activate it and install requirements
. venv/bin/activate

if [ -f requirements.txt ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, skipping pip install."
fi

# 4) Load env variables from .env
if [ -f .env ]; then
    echo "🌱 Loading environment variables from .env..."
    while IFS='=' read -r key value; do
        if [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
            export "$key=$value"
        fi
    done < .env
fi

# Load flags from .flags
FLAGS=""
if [ -f .flags ]; then
    echo "🎯 Loading flags from .flags..."
    FLAGS=$(cat .flags)
fi

# Run main.py
echo "🚀 Running main.py..."
venv/bin/python {} $FLAGS
"""


hashfind = """
#!/bin/bash
find . -type f ! -path "./venv/*" ! -path "./logs/*" | while read -r file; do
    hash=$(sha256sum "$file" | awk '{print $1}')
    relpath="${file#./}"  # remove leading ./ for clean output
    echo "$relpath=$hash"
done
"""
