#!/bin/bash
# ==============================================================================
# PhotoTochka VDS Deployment Script
#   - Собирает фронт и статику ЛОКАЛЬНО
#   - Синхронизирует код на VDS через rsync
#   - Генерирует .env для продакшена (при первом деплое)
#   - Собирает Docker-образы и запускает сервисы на VDS
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT"

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "${PHOTO_DEPLOY_HOST:-}" ]; then
    echo "❌ PHOTO_DEPLOY_HOST не задан в .env"
    exit 1
fi

PHOTO_DEPLOY_USER=${PHOTO_DEPLOY_USER:-"root"}
PHOTO_DEPLOY_PATH=${PHOTO_DEPLOY_PATH:-"/opt/phototochka"}

echo "🚀 Деплой на $PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST"

# ─── 1. Сборка фронта и статики ────────────────────────────────────────────────
if [ "${PHOTO_DEPLOY_SKIP_BUILD:-0}" != "1" ]; then
    echo "🏗️  Сборка фронтенда (vite build)..."
    (cd "$ROOT/frontend" && npm ci && npx vite build && cp dist/index.html dist/404.html)

    echo "🏗️  Сборка статики Django (collectstatic)..."
    if [ ! -d "$ROOT/backend/.venv" ]; then
        echo "   Создаю venv и ставлю зависимости..."
        (cd "$ROOT/backend" && python3 -m venv .venv && .venv/bin/pip install -U pip -q && .venv/bin/pip install -r requirements.txt)
    fi
    (cd "$ROOT/backend" && .venv/bin/python manage.py collectstatic --noinput)
else
    echo "⏭️  Сборка пропущена (PHOTO_DEPLOY_SKIP_BUILD=1)"
fi

# ─── 2. Подготовка VDS ──────────────────────────────────────────────────────────
echo "🧹 Подготовка VDS..."
ssh "$PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST" "mkdir -p $PHOTO_DEPLOY_PATH"

# ─── 3. Синхронизация кода ──────────────────────────────────────────────────────
echo "📤 Синхронизация через rsync..."
rsync -avz --progress \
    --exclude='.git/' \
    --exclude='.cursor/' \
    --exclude='docs/' \
    --exclude='frontend/node_modules/' \
    --exclude='backend/.venv/' \
    --exclude='backend/db.sqlite3' \
    --exclude='backend/media/' \
    --exclude='**/__pycache__/' \
    --exclude='.env' \
    ./ "$PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST:$PHOTO_DEPLOY_PATH/"

# Примечание: frontend/dist/ и backend/staticfiles/ НЕ исключены — они нужны nginx

# ─── 4. Генерация .env на VDS (только если нет) ────────────────────────────────
echo "📋 Настройка .env на VDS..."
if ! ssh "$PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST" "test -f $PHOTO_DEPLOY_PATH/.env"; then
    echo "   Генерирую production .env..."
    SECRET_KEY=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=' | head -c50)
    ssh "$PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST" "cat > $PHOTO_DEPLOY_PATH/.env" << ENVEOF
DJANGO_SECRET_KEY=$SECRET_KEY
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=$PHOTO_DEPLOY_HOST,localhost
DATABASE_URL=postgres://user:password@db:5432/phototochka
CORS_ALLOWED_ORIGINS=
VITE_API_URL=
SEED_ADMIN_EMAIL=admin@phototochka.ru
SEED_ADMIN_PASSWORD=$(openssl rand -base64 12)
PHOTO_DEPLOY_HOST=$PHOTO_DEPLOY_HOST
PHOTO_DEPLOY_USER=$PHOTO_DEPLOY_USER
PHOTO_DEPLOY_PATH=$PHOTO_DEPLOY_PATH
ENVEOF
    echo "   ✅ .env создан"
else
    echo "   .env уже существует (оставлен без изменений)"
fi

# ─── 5. Сборка и деплой на VDS ─────────────────────────────────────────────────
echo "🔨 Сборка и запуск на VDS..."
ssh "$PHOTO_DEPLOY_USER@$PHOTO_DEPLOY_HOST" "bash -s" << EOF
    set -e
    cd $PHOTO_DEPLOY_PATH

    echo "🏗️  Docker build..."
    DOCKER_BUILDKIT=1 docker compose -f docker-compose.prod.yml build

    echo "⬇️  Остановка старых контейнеров..."
    docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

    echo "🔄 Миграции..."
    docker compose -f docker-compose.prod.yml run --rm backend python manage.py migrate --noinput

    echo "🌱 Сид демо-данных..."
    docker compose -f docker-compose.prod.yml run --rm backend python manage.py seed_demo

    echo "⬆️  Запуск контейнеров..."
    docker compose -f docker-compose.prod.yml up -d --force-recreate

    echo '📊 Статус:'
    docker compose -f docker-compose.prod.yml ps
EOF

echo ""
echo "✅ Деплой завершён!"
echo "🌐 http://$PHOTO_DEPLOY_HOST"
