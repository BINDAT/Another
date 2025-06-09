#!/bin/bash

set -e

echo "🔄 Sauvegarde de /etc/apt/sources.list en /etc/apt/sources.list.bak"
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bak

echo "🧹 Nettoyage et réécriture du fichier /etc/apt/sources.list"
sudo tee /etc/apt/sources.list > /dev/null << 'EOF'
# Dépôt principal Debian 12 (Bookworm)
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware

# Mises à jour de sécurité
deb http://security.debian.org/debian-security bookworm-security main contrib non-free-firmware

# Mises à jour stables (patchs mineurs)
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware

# (Optionnel) Sources - décommentez si nécessaire
# deb-src http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
# deb-src http://security.debian.org/debian-security bookworm-security main contrib non-free-firmware
# deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
EOF

echo "✅ Fichier corrigé. Mise à jour des dépôts..."
sudo apt update

echo "🎉 Terminé. Votre sources.list est propre et fonctionnel."