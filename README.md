# UCSE-2025-IW-TP-G7-Fornari_Gigon_Pluda

---

## 🛠️ Justificación del Proyecto

### 📌 Necesidad real

La ciudad de Rafaela carece de una herramienta centralizada y accesible que permita consultar los horarios y ubicaciones de misas, adoraciones, confesiones y otros eventos parroquiales. Actualmente, los fieles deben buscar esta información en múltiples fuentes: redes sociales, grupos privados, estados de WhatsApp o contactos personales. Esta dispersión dificulta la participación activa en la vida litúrgica y comunitaria.

---

### 🎯 Problema a resolver

Los usuarios enfrentan una búsqueda fragmentada y poco eficiente de eventos religiosos. La información suele estar distribuida en perfiles de Instagram, carteleras físicas o mensajes informales, lo que impide una planificación clara y rápida. Nuestra solución propone una aplicación web responsive que centraliza esta información, permitiendo consultar actividades por tipo, fecha y ubicación, sin necesidad de registro ni conocimientos técnicos.

---

### 💡 Alternativas existentes y ventajas competitivas

**Alternativas actuales:**
- Redes sociales (Instagram, Facebook, WhatsApp)
- Carteleras físicas en parroquias
- Comunicación boca a boca

**Ventajas de nuestra propuesta:**
- Acceso libre y sin registro
- Visualización clara por día y horario
- Filtros por tipo de evento y ubicación
- Información actualizada desde una hoja de cálculo dinámica
- Posibilidad de agregar eventos especiales (bingo, grupos juveniles, etc.)
- Exportación futura a PDF o integración con calendarios personales

---

### 👥 Usuarios objetivo

- **Fieles activos (30–65 años):** buscan participar en misas y adoraciones sin depender de redes sociales.
- **Jóvenes católicos (15–30 años):** interesados en grupos juveniles, confesiones y eventos comunitarios.
- **Organizadores parroquiales:** necesitan difundir actividades especiales como bingos, retiros o celebraciones.

---

### 🧭 Escenario de uso central

Un usuario accede a la aplicación desde su celular sin necesidad de registrarse. En la pantalla principal ve los eventos del día ordenados por horario, con detalles como tipo de actividad, parroquia y notas adicionales (ej. “Misa + Adoración”). Puede seleccionar otro día desde una grilla horizontal o desde un calendario para consultar eventos futuros. También puede acceder al apartado de parroquias para ver ubicación, contactos e imágenes, o visitar la sección de noticias para enterarse de eventos especiales.

---

### ⚙️ Funcionamiento técnico

La aplicación se alimenta de una hoja de cálculo dinámica en Google Sheets, dividida en:
- **Actividades permanentes:** eventos que se repiten semanalmente.
- **Eventos especiales:** actividades únicas o mensuales (ej. “Primer domingo del mes”).

La hoja se publica en modo lectura, permitiendo que el sitio web consuma los datos actualizados sin exponer credenciales ni permitir edición pública. Se utilizan macros y filtros para mantener el orden por fecha y horario.

---

### 🎯 Qué se espera

Se espera que la comunidad católica de Rafaela utilice esta herramienta como sitio centralizado para consultar y difundir actividades litúrgicas y comunitarias, facilitando la participación y la organización.

---

### ❤️ Motivación

La motivación principal es **reducir la dispersión de información** y **facilitar el acceso a eventos religiosos**. Hoy en día, los fieles deben seguir múltiples cuentas en redes sociales o depender de contactos personales para enterarse de los horarios. Esta aplicación busca **democratizar el acceso**, **simplificar la búsqueda** y **fortalecer la vida comunitaria**.
