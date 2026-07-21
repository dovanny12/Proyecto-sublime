# Sublime OSC - Tienda de Sublimación

Sistema de compra/venta de productos sublimados con panel de administración.

## Requisitos

- Python 3.12+
- pip

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar

```bash
python pagina-web-sublime/app.py
```

Abrir http://127.0.0.1:5000

## Admin

http://127.0.0.1:5000/admin

- adminsublime@gmail.com / watsonamelia12 (Administrador Panel)
- admin_web@sublime.com / adminweb123 (Administrador Web)

## Estructura

```
pagina-web-sublime/   → Tienda web (app Flask, templates, static)
Sublime/
  admin-panel/        → Panel de administración
  BD/                 → Base de datos compartida
```
