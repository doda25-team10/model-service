# ---- Stage 1: Builder ----
FROM python:3.12-slim AS builder

WORKDIR /root/sms

# Install build dependencies without leaving apt cache
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies in isolated folder
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Copy source code
COPY src/ src/
COPY smsspamcollection/ smsspamcollection/

# ---- Stage 2: Final image ----
FROM python:3.12-slim

WORKDIR /root/sms

ENV PORT=8081

# Copy only installed Python packages (no apt cache)
COPY --from=builder /install /usr/local

# Copy source code
COPY --from=builder /root/sms/src ./src
COPY --from=builder /root/sms/smsspamcollection ./smsspamcollection

EXPOSE ${PORT}

# Run the app
CMD ["sh", "-c", "python src/serve_model.py --port ${PORT}"]
