FROM ubuntu:24.04

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install all conversion tools and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    dpkg-dev \
    rpm \
    file \
    binutils \
    squashfs-tools \
    ruby-full \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install FPM for cross-architecture RPM building
RUN gem install --no-document fpm

# Verify installations
RUN echo "Build tools installed:" && \
    dpkg-deb --version | head -1 && \
    rpmbuild --version | head -1 && \
    fpm --version && \
    python3 --version

# Set working directory
WORKDIR /workspace

# Label the image
LABEL org.opencontainers.image.source="https://github.com/DevelopmentCats/AppBinHub"
LABEL org.opencontainers.image.description="AppBinHub converter image with all build tools pre-installed"
LABEL org.opencontainers.image.licenses="MIT"
