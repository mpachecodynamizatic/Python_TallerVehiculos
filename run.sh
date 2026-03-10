#!/bin/bash
# Script para ejecutar el proyecto Django - Taller de Vehiculos
# Uso: ./run.sh

echo "========================================"
echo "  Sistema de Gestion de Taller"
echo "  Django 6.0 + HTMX + Alpine.js"
echo "========================================"
echo ""

# Activar entorno virtual
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
    echo "[OK] Entorno virtual activado"
elif [ -f .venv/Scripts/activate ]; then
    source .venv/Scripts/activate
    echo "[OK] Entorno virtual activado"
else
    echo "[ERROR] No se encuentra el entorno virtual .venv"
    echo "Ejecuta: python -m venv .venv"
    exit 1
fi

# Verificar que Django esta instalado
python -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "[ADVERTENCIA] Django no esta instalado"
    echo "Instalando dependencias..."
    pip install -r requirements/base.txt
fi

echo ""
echo "[*] Verificando configuracion del proyecto..."
python manage.py check
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Hay problemas con la configuracion del proyecto"
    exit 1
fi

echo ""
echo "========================================"
echo "  Iniciando servidor de desarrollo"
echo "========================================"
echo ""
echo "[*] Servidor disponible en: http://localhost:8000"
echo "[*] Admin panel en: http://localhost:8000/admin"
echo "[*] Dashboard en: http://localhost:8000/dashboard"
echo ""
echo "Credenciales:"
echo "  Usuario: admin"
echo "  Password: Admin1234!"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python manage.py runserver
