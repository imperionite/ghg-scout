#!/usr/bin/env bash

# Exit on any error
set -o errexit

# Create virtual environment with Python 3.9.12
echo "🔹 Creating virtual environment with Python 3.9.X..."
python -m venv venv

# Activate virtual environment
echo "🔹 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔹 Upgrading pip..."
pip install --upgrade pip

# Install packages without versions so pip resolves compatible ones
echo "🔹 Installing packages..."
pip install \
annotated-types \
anyio \
autopep8 \
bcrypt \
certifi \
charset-normalizer \
click \
dnspython \
Faker \
fastapi \
fastapi-cache2 \
filelock \
fsspec \
h11 \
hf-xet \
httptools \
huggingface-hub \
idna \
Jinja2 \
MarkupSafe \
motor \
mpmath \
networkx \
numpy \
packaging \
pendulum \
pycodestyle \
pydantic \
pydantic_core \
pymongo \
python-dateutil \
python-dotenv \
PyYAML \
regex \
requests \
safetensors \
six \
sniffio \
starlette \
sympy \
tokenizers \
torch \
tqdm \
transformers \
typing-inspection \
typing_extensions \
tzdata \
urllib3 \
uvicorn \
uvloop \
watchfiles \
websockets

# Save resolved versions
echo "🔹 Exporting resolved requirements to requirements.txt..."
pip freeze > requirements.txt

echo "✅ Installation complete. Virtual environment ready!"
