# Base educativa — COMP 2700

Esta versión contenia debilidades intencionales, los cuales se corrigieron en esta version del proyecto. Utilice únicamente los datos ficticios incluidos, en su computadora. No es una aplicación de producción.

---

## Estudiante y Datos del Proyecto
* **Nombre:** Edward A. Navarreto Lassalle
* **Curso:** COMP 2700
* **Repositorio:** CyberMiniProy (Prototipo de Inventario Seguro)

---

## Requisitos y Ejecución

Requiere Python 3.10 o posterior. Desde esta carpeta:

```bash
python -m venv .venv
```

Windows CMD:
```cmd
.venv\Scripts\activate.bat
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Luego:
```bash
python -m pip install -r requirements.txt
python app.py
```

*(En algunos sistemas debe utilizar `python3` en lugar de `python`).*

### Dependencias principales
* `argon2-cffi` (incluida en `requirements.txt` para la verificación segura de credenciales).

---

## Cuentas públicas y exclusivamente ficticias
* `admin` / `AdminDemo2700!`
* `user` / `UserDemo2700!`

Comience probando consulta y cambio de cantidad con `admin`. La base no aplica todos los controles: `user` también puede modificar, las claves están legibles, las entradas inválidas pueden causar errores y no se guarda auditoría. Los `TODO` de `app.py` guían las correcciones; `seguridad.py` contiene funciones listas.

---

## Notas Técnicas de Arquitectura y Migración

Para migrar las contraseñas, cree un pequeño script que llame `crear_hash` para cada cuenta y guarde el resultado en un campo `hash`. Elimine el campo `clave` del archivo final. Adapte `autenticar` para llamar `verificar_clave`. No compare dos hashes recién generados: sus salts serán diferentes.

Los archivos se resuelven respecto a `app.py`. Guarde una copia del inventario antes de las pruebas de errores. Use `P001` con cantidad `10` al comenzar.

Puede hacer pruebas directas desde un script que importe `app`:

```python
import app
sesion = app.autenticar("user", "UserDemo2700!")
app.modificar_cantidad(sesion, "P001", "99")
```

Después de corregir los permisos, esa llamada debe rechazarse sin cambiar `P001`. Repita con `None` como sesión. No fabrique un diccionario con rol `admin` para simular una sesión válida: esta aplicación confía en su propio proceso.

JSON almacena un documento completo (lista de productos o usuarios). Solamente `auditoria.jsonl` utiliza un objeto por línea.

---

## Evidencia de Ejecución y Pruebas Realizadas

Se ejecutaron y validaron localmente los siguientes controles de seguridad y manejo de errores:
1. **Control de Acceso (RBAC) y Sesiones:** Verificación de que sesiones nulas (`None`) o usuarios con rol `user` son rechazados al intentar modificar el inventario (`modificar_cantidad`), registrando el evento de rechazo en `auditoria.jsonl`.
2. **Validación de Entradas Numéricas:** Pruebas con valores fuera de rango (`-1`, `1001`), cadenas de texto (`abc`), flotantes (`2.5`) y entradas vacías, asegurando su rechazo controlado sin alterar el archivo `inventario.json`, y confirmando la aceptación de los límites inclusivos (`0` y `1000`).
3. **Integridad y Manejo de Productos Inexistentes:** Modificación exitosa de `P001` como `admin` y rechazo controlado al intentar modificar un ID inexistente (`P999`) sin crear registros fantasma.
4. **Persistencia y Manejo de Errores de Archivo:** Comprobación de persistencia tras reiniciar el programa y manejo seguro de excepciones ante ausencia de `inventario.json` (`FileNotFoundError`) o contenido corrupto literal (`ESTO NO ES JSON` / `JSONDecodeError`), restaurando mediante respaldo sin sobrescribir datos.
5. **Auditoría (`auditoria.jsonl`):** Registro cronológico en formato JSONL de inicios de sesión (exitosos y fallidos) y modificaciones (autorizadas y denegadas), excluyendo contraseñas y hashes.
6. **Portabilidad:** Clonación del repositorio en un directorio limpio independiente y ejecución exitosa siguiendo exclusivamente las instrucciones de este documento.

---

## Fuentes y Uso de Inteligencia Artificial
* **Fuentes consultadas:** Documentación oficial de Python 3 (módulos `json`, `pathlib`, `datetime`) y material base proporcionado en el curso COMP 2700 (`app.py` y `seguridad.py`).
* **Herramientas de IA utilizadas:** Se utilizó el asistente de inteligencia artificial **Gemini** como apoyo técnico para estructurar el manejo de excepciones (`JSONDecodeError`), refinar la lógica de validación de rangos numéricos y organizar el formato de registros JSONL en `auditoria.jsonl`.
* **Verificación:** Todas las sugerencias generadas fueron probadas y depuradas manualmente en la terminal de Linux mediante casos de prueba límite (entradas inválidas, sesiones nulas y archivos corruptos) para asegurar su funcionamiento exacto conforme a las reglas del proyecto.
## Referencias y Fuentes

* **OWASP Foundation.** (2021). *OWASP Top Ten: The Ten Most Critical Web Application Security Risks*. Open Worldwide Application Security Project (OWASP). [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)
* **National Institute of Standards and Technology (NIST).** (2020). *Digital Identity Guidelines* (NIST Special Publication 800-63B). U.S. Department of Commerce.
---

## Limitaciones del Prototipo
Los permisos y validaciones se aplican únicamente dentro de la lógica de ejecución del programa. Una persona con acceso de lectura y escritura a los archivos locales (`inventario.json`, `usuarios.json`, `auditoria.jsonl`) puede alterarlos directamente desde el sistema operativo. Este prototipo no implementa cifrado de datos en reposo, protección a nivel de sistema operativo, recuperación de contraseñas, autenticación multifactor (MFA) ni protección criptográfica del log contra modificaciones externas.

---

*Nota de entrega: No suba `.venv`, `__pycache__`, credenciales reales ni datos personales de terceros.*