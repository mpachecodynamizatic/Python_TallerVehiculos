# 🚀 Inicio Rápido - 2 Pasos

## ⚡ Opción 1: Super Rápido (TODO EN UNO)

**Doble click en:**
```
iniciar.bat
```

Este script hace TODO automáticamente:
- ✅ Detecta y activa el entorno virtual
- ✅ Instala Django si no está
- ✅ Verifica la configuración
- ✅ Inicia el servidor

Luego abre: http://localhost:8000/admin

---

## 🧪 Opción 2: Probar Primero

### Paso 1: Probar

**Doble click en:**
```
probar.bat
```

Verifica que todo funciona:
- ✅ Encuentra el entorno virtual
- ✅ Django instalado
- ✅ Proyecto configurado correctamente
- ✅ Todos los archivos en su lugar

### Paso 2: Iniciar

**Doble click en:**
```
iniciar.bat
```

---

## 🌐 Abrir en el Navegador

Una vez iniciado el servidor, abre:

### 👨‍💼 Panel de Administración ⭐
http://localhost:8000/admin

### 📊 Dashboard
http://localhost:8000/dashboard

### 🏠 Inicio
http://localhost:8000

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

---

## 📂 Scripts Disponibles

| Script | Qué hace |
|--------|----------|
| **iniciar.bat** ⭐ | Inicia todo automáticamente |
| **probar.bat** | Verifica que todo funcione |
| **run.bat** | Inicia solo el servidor |
| **test_simple.bat** | Prueba detallada |

---

## ❌ Solución de Problemas

### "No se encuentra el entorno virtual"
El script `iniciar.bat` te preguntará si quieres crearlo automáticamente.

O manualmente:
```cmd
python -m venv .venv
```

### "Django no instalado"
El script `iniciar.bat` lo instalará automáticamente.

O manualmente:
```cmd
.venv\Scripts\activate
pip install -r requirements\base.txt
```

### "El puerto está en uso"
Cierra otros servidores Python o usa otro puerto:
```cmd
python manage.py runserver 8001
```

---

## 📞 Comandos Manuales (Avanzado)

Si prefieres hacerlo manualmente:

```cmd
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Verificar Django
python -c "import django; print(django.get_version())"

# 3. Verificar proyecto
python manage.py check

# 4. Iniciar servidor
python manage.py runserver
```

---

## ✅ ¿Qué deberías ver?

### En el Admin (http://localhost:8000/admin):
- ✅ Formulario de login de Django
- ✅ Puedes entrar con admin/admin123
- ✅ Ves "AUTHENTICATION AND AUTHORIZATION"
- ✅ Puedes ver Users y Groups

### En el Dashboard (http://localhost:8000/dashboard):
- ✅ Barra de navegación azul con logo "🚗 Taller"
- ✅ 4 tarjetas de estadísticas (todas en 0):
  - Total Clientes: 0
  - Citas Hoy: 0
  - Órdenes Activas: 0
  - Facturación del Mes: €0
- ✅ Tarjeta de bienvenida "¡Proyecto Configurado Exitosamente!"
- ✅ Checkmarks: Django ✓ HTMX ✓ Alpine.js ✓ Tailwind CSS ✓

---

## 🎯 Primer Inicio Recomendado

```
1. Doble click en: probar.bat
   (Verifica que todo esté bien)

2. Si todo OK, doble click en: iniciar.bat
   (Inicia el servidor)

3. Abre tu navegador en: http://localhost:8000/admin
   (Login con admin/admin123)

4. ¡Listo! FASE 0 completada ✅
```

---

**¿Necesitas más ayuda?** Revisa [COMO_PROBAR.md](COMO_PROBAR.md) para detalles completos.
