#!/usr/bin/env bash
#
# Publica o site institucional no container do Proxmox.
#
# O site é uma página só mais as fotos que ela usa, servidas por nginx. O
# deploy, portanto, é copiar esses arquivos para dentro do container e conferir
# que o nginx continua de pé — não há build, não há dependência, não há passo
# que possa falhar pela metade.
#
# As fotos vão primeiro, e a página depois: na ordem inversa, o visitante que
# chegasse no meio da publicação veria o layout novo com os quadros vazios.
#
#   ./deploy.sh              # publica
#   ./deploy.sh --dry-run    # mostra o que faria, sem tocar em nada
#
# O que ele NÃO faz, de propósito: instalar nginx, criar o container, mexer em
# TLS ou em DNS. Essas são decisões de infraestrutura, e um script de publicação
# que também provisiona servidor é um script que ninguém lê antes de rodar.

set -euo pipefail

# ─── O que muda por ambiente ─────────────────────────────────────────────
PVE_HOST="${PVE_HOST:-root@192.168.100.20}"   # host Proxmox (não o container)
CT_ID="${CT_ID:-300}"                          # o container do site
# Onde o nginx do container procura os arquivos — conferido no CT 300.
REMOTE_ROOT="${REMOTE_ROOT:-/var/www/belia-site}"

LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$LOCAL_DIR/mishpat/index.html"
# O site é servido da raiz do domínio, e é lá que o arquivo vive.
TARGET="$REMOTE_ROOT/index.html"
# As fotos ficam ao lado da página, no caminho que o HTML escreve (assets/…).
ASSETS_DIR="$LOCAL_DIR/mishpat/assets"
ASSETS_TARGET="$REMOTE_ROOT/assets"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

run() {
  if $DRY_RUN; then
    printf '  [dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

echo "Publicando o site"
echo "  origem:    $SOURCE"
echo "  destino:   CT $CT_ID em $PVE_HOST → $TARGET"
echo

[[ -f "$SOURCE" ]] || { echo "erro: $SOURCE não existe" >&2; exit 1; }

# A configuração de produção precisa estar apontando para o domínio real, e
# não para a máquina de quem publicou. Barato de conferir, caro de descobrir
# depois — foi exatamente isso que deixou a página sem os planos uma vez.
if grep -q "apiUrl: 'http://localhost" "$SOURCE"; then
  echo "erro: o bloco window.BELIA está com endereço local no lugar do de produção." >&2
  echo "      Ajuste appUrl/apiUrl no topo de mishpat/index.html antes de publicar." >&2
  exit 1
fi

# O container precisa estar de pé antes de qualquer cópia.
STATUS="$(ssh "$PVE_HOST" "pct status $CT_ID" 2>/dev/null || true)"
case "$STATUS" in
  *running*) echo "container $CT_ID: no ar" ;;
  "")        echo "erro: não consegui falar com $PVE_HOST." >&2; exit 1 ;;
  *)         echo "erro: container $CT_ID não está rodando ($STATUS)." >&2; exit 1 ;;
esac

# A cópia vai para o host e de lá para dentro do container: `pct push` não lê
# arquivo da máquina local.
run ssh "$PVE_HOST" "pct exec $CT_ID -- mkdir -p $ASSETS_TARGET"

# As fotos primeiro. `pct push` é um arquivo por vez, e são poucos — um laço
# aqui se lê melhor do que empacotar e desempacotar do outro lado.
if [[ -d "$ASSETS_DIR" ]]; then
  echo "→ enviando as fotos ($(ls -1 "$ASSETS_DIR" | wc -l | tr -d ' ') arquivos)"
  for asset in "$ASSETS_DIR"/*; do
    [[ -f "$asset" ]] || continue
    name="$(basename "$asset")"
    staging="/tmp/belia-asset-$$-$name"
    run scp -q "$asset" "$PVE_HOST:$staging"
    run ssh "$PVE_HOST" "pct push $CT_ID $staging $ASSETS_TARGET/$name --perms 644"
    run ssh "$PVE_HOST" "rm -f $staging"
  done
fi

STAGING="/tmp/belia-site-$$.html"
echo "→ enviando a página para o host"
run scp -q "$SOURCE" "$PVE_HOST:$STAGING"

echo "→ colocando no container"
run ssh "$PVE_HOST" "pct push $CT_ID $STAGING $TARGET --perms 644"
run ssh "$PVE_HOST" "rm -f $STAGING"

# Recarregar, e não reiniciar: reload troca a configuração sem derrubar quem
# está com a página aberta. E só depois de o nginx dizer que a configuração
# está válida — recarregar configuração quebrada tira o site do ar.
echo "→ recarregando o nginx"
run ssh "$PVE_HOST" "pct exec $CT_ID -- nginx -t"
run ssh "$PVE_HOST" "pct exec $CT_ID -- systemctl reload nginx"

echo
if $DRY_RUN; then
  echo "nada foi alterado (--dry-run)."
else
  echo "publicado."
fi
