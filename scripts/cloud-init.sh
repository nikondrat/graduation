#!/bin/sh
# ==============================================================================
# PhotoTochka — Cloud-init для Timeweb VDS
# Вставьте этот скрипт в поле «Cloud-init» при создании сервера (Ubuntu 22.04+)
# ==============================================================================

set -e

# 1. System update
apt-get -y update
apt-get -y upgrade

# 2. Install Docker + Compose V2
apt-get -y install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get -y update
apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable docker

# 3. UFW: только 22 (SSH), 80 (HTTP), 443 (HTTPS)
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 4. Swap 2GB (для 1GB VDS — спасает при docker build)
if [ ! -f /swapfile ]; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 5. Подсказка (будет видна после первого входа)
echo ""
echo "============================================"
echo "  PhotoTochka VDS готов!"
echo "  Следующие шаги:"
echo "  1. Убедитесь, что SSH-ключ добавлен:"
echo "     ssh-copy-id root@<IP-сервера>"
echo "  2. На локальной машине в корне проекта:"
echo "     echo 'PHOTO_DEPLOY_HOST=<IP-сервера>' >> .env"
echo "     ./photo deploy"
echo "============================================"
