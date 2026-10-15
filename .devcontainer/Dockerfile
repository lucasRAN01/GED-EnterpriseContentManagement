FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# L'image de base déclare le dépôt apt de yarn, dont la clé a expiré :
# « apt-get update » échoue et bloque la fonctionnalité Docker-in-Docker.
# Yarn n'est pas utilisé ici, on retire donc ce dépôt.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && sed -i '/dl\.yarnpkg\.com/d' /etc/apt/sources.list /etc/apt/sources.list.d/*.list 2>/dev/null || true
