# OSIA Container with Graviton Support
# Based on Universal Base Image for RHEL 9
FROM registry.access.redhat.com/ubi9/ubi:latest

# Set labels
LABEL name="osia" \
      version="0.2.0-alpha16" \
      description="OpenShift Infrastructure Automation"

# Install required packages
RUN dnf update -y && \
    dnf install -y --allowerasing \
    python3.11 \
    python3.11-pip \
    python3.11-devel \
    git \
    bind-utils \
    curl \
    wget \
    unzip \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.11 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN poetry env use python3.11 && \
        poetry install --only=main

# Create directories for installers and clusters
RUN mkdir -p /app/installers /app/clusters

# Set environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app"

# Create a non-root user for security
RUN useradd -m -u 1001 osia && \
    chown -R osia:osia /app

# Switch to non-root user
USER osia

# Set working directory
WORKDIR /app

# Default command
CMD ["poetry", "run", "osia", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD poetry run osia --help > /dev/null || exit 1
