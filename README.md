# 🏋️ Gym Management Dashboard

Un sistema web dinámico e interactivo diseñado para la gestión integral de un centro de entrenamiento. Desarrollado como **Proyecto Final para CS50x (Harvard University)**.

🎬 **Video Demostrativo:** [Ver demo en YouTube](AQUÍ_TU_LINK_DE_YOUTUBE)

---

📌 Descripción y Problema que Resuelve

Esta aplicación resuelve la administración diaria de un gimnasio permitiendo a los administradores gestionar clientes, membresías, asistencias y cobros de manera centralizada. Incorpora lógica de negocio para el cálculo de recargos, control de vencimientos y generación de métricas de uso.

---

✨ Características Principales

- 🔐 **Autenticación y Seguridad:** Sistema de inicio de sesión y registro de usuarios con contraseñas encriptadas (*hash*).
- 📊 **Panel de Control (Dashboard):** Vista general con métricas clave de socios activos, pagos pendientes y asistencias del día.
- 💳 **Gestión de Membresías y Pagos:** Módulo para registrar cuotas, vencimientos y recargos dinámicos.
- 🗄️ **Base de Datos Relacional:** Estructura optimizada para la integridad de los datos de socios, planes y transacciones.
- 📱 **Interfaz Adaptativa:** Maquetación limpia y responsive para fácil acceso desde dispositivos móviles o tablets.

---

🛠️ Tecnologías Utilizadas

- **Back-end:** Python, Flask (Framework web).
- **Base de Datos:** SQL / SQLite.
- **Front-end:** HTML5, CSS3, JavaScript, Bootstrap 5.
- **Herramientas:** Git, CS50 Library, Jinja2 (Templating).

---

📂 Estructura del Repositorio

```text
├── static/         # Archivos CSS, JS e imágenes
├── templates/      # Plantillas Jinja2 (HTML)
├── app.py          # Servidor principal y rutas en Flask
├── helpers.py      # Funciones auxiliares y decoradores
├── project.db      # Base de datos SQLite
└── README.md       # Documentación del proyecto
```
---

## 🐳 Cómo ejecutar con Docker

## 🐳 Cómo ejecutar con Docker

1. Construir la imagen:
```bash
    docker build -t gym-app .
```

2. Inicial el contenedor:
```bash
    docker run -p 5000:5000 gym-app
```

3. Abrir en el navegador: `http://localhost:5000`
---

👨‍💻 Autor

Iván Tuamá
- GitHub: https://github.com/IvanTuama98
- LinkedIn: https://www.linkedin.com/in/ivantuama
