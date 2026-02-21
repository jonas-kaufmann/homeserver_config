FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY hetzner_ddns.py .
COPY fritzbox.py .

# Run the script every 60 seconds with bash loop
CMD ["bash", "-c", "while true; do python hetzner_ddns.py; sleep 60; done"]
