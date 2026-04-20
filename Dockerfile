FROM python:3.12-slim

WORKDIR /app

# Install notebooklm-py and server dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium for notebooklm-py
RUN playwright install chromium --with-deps

COPY server.py .

EXPOSE 8484

CMD ["python", "server.py", "--sse"]
