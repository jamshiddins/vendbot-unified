# 🚀 VendBot Production Deployment Guide

## Prerequisites

- VPS with Ubuntu 22.04 LTS
- Domain name pointed to server IP
- SSL certificate (Let's Encrypt recommended)
- Docker and Docker Compose installed

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment user
sudo useradd -m -s /bin/bash vendbot
sudo usermod -aG docker vendbot
sudo su - vendbot