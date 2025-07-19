# 📚 Guía Completa de Configuración de GitHub para GENESIS NGX

## 🎯 ¿Qué vamos a hacer y por qué?

Vamos a configurar medidas de seguridad y automatización en tu repositorio de GitHub para:

1. **Proteger tu código** - Evitar cambios accidentales en producción
2. **Automatizar publicaciones** - El SDK se publicará automáticamente a npm
3. **Mantener calidad** - Los tests se ejecutarán automáticamente
4. **Trabajo en equipo** - Facilitar colaboración segura

## 📋 Paso 1: Protección de Branches (Ramas)

### ¿Qué es la protección de branches?

Es como poner un candado a las ramas importantes (main, staging) para que nadie pueda hacer cambios directamente sin revisión. Todos los cambios deben pasar por un Pull Request (PR) que alguien más revise.

### Pasos detallados:

1. **Ve a tu repositorio en GitHub**
   ```
   https://github.com/270aldo/Genesis_NGX_1.0
   ```

2. **Haz clic en "Settings" (Configuración)**
   - Está en la barra superior del repositorio
   - Icono de engranaje ⚙️

3. **En el menú izquierdo, busca "Branches"**
   - Está bajo la sección "Code and automation"

4. **Haz clic en "Add rule" (Agregar regla)**

5. **Configura la protección para la rama `main`:**
   
   **Branch name pattern:** `main`
   
   **Marca estas opciones:**
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1 (mínimo 1 persona debe aprobar)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
   
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Busca y selecciona estos checks:
       - `backend-tests`
       - `frontend-tests`
       - `security-scan`
   
   - ✅ **Require conversation resolution before merging**
   
   - ✅ **Include administrators** (opcional, pero recomendado)

6. **Haz clic en "Create" al final**

7. **Repite el proceso para la rama `staging`:**
   - Haz clic en "Add rule" nuevamente
   - Branch name pattern: `staging`
   - Usa las mismas configuraciones que para `main`

## 📋 Paso 2: Configurar Secrets (Variables Secretas)

### ¿Qué son los secrets?

Son como contraseñas que tu código necesita pero que no quieres que sean públicas. Por ejemplo, la clave para publicar en npm o credenciales de bases de datos.

### Pasos detallados:

1. **En Settings, busca "Secrets and variables" en el menú izquierdo**
   - Haz clic en "Actions"

2. **Haz clic en "New repository secret"**

3. **Agrega el secret para NPM (para publicar el SDK):**
   
   **Name:** `NPM_TOKEN`
   
   **Secret:** (Necesitas obtener esto de npm)
   
   ### Cómo obtener tu NPM_TOKEN:
   
   a. Ve a https://www.npmjs.com/
   b. Inicia sesión o crea una cuenta
   c. Haz clic en tu avatar → "Access Tokens"
   d. Clic en "Generate New Token" → "Classic Token"
   e. Selecciona "Automation" como tipo
   f. Copia el token generado
   g. Pégalo en el campo Secret en GitHub
   h. Clic en "Add secret"

4. **Agrega otros secrets necesarios** (uno por uno):

   **Para Google Cloud:**
   - **Name:** `GOOGLE_APPLICATION_CREDENTIALS_BASE64`
   - **Secret:** (Necesitas codificar tu archivo credentials.json en base64)
   
   ```bash
   # En tu terminal, ejecuta:
   base64 -i backend/credentials.json | pbcopy
   # Esto copia el contenido codificado al portapapeles
   ```

   **Para Supabase:**
   - **Name:** `SUPABASE_URL`
   - **Secret:** `tu-url-de-supabase`
   
   - **Name:** `SUPABASE_ANON_KEY`
   - **Secret:** `tu-clave-anonima-de-supabase`

   **Para JWT:**
   - **Name:** `JWT_SECRET_KEY`
   - **Secret:** `una-clave-secreta-muy-segura-123`

## 🔍 Verificación

### Para verificar la protección de branches:

1. Intenta editar un archivo directamente en la rama `main` en GitHub
2. GitHub no te dejará hacer commit directo
3. Te pedirá crear un Pull Request

### Para verificar los secrets:

1. Ve a Actions → Puedes ver la lista de secrets (pero no sus valores)
2. Los workflows de GitHub Actions podrán usarlos automáticamente

## 🚀 ¿Qué sigue después?

Una vez configurado esto:

1. **Los tests se ejecutarán automáticamente** cuando hagas push
2. **Nadie podrá romper main accidentalmente** 
3. **El SDK se publicará automáticamente** cuando crees un tag de versión
4. **Tendrás un flujo de trabajo profesional**

## 📝 Flujo de trabajo recomendado:

1. Siempre trabaja en la rama `develop`
2. Cuando tengas algo listo, crea un PR a `staging`
3. Después de probar en staging, crea un PR a `main`
4. Para publicar una nueva versión:
   ```bash
   git tag v1.0.0
   git push --tags
   ```

## ❓ Preguntas Frecuentes

**P: ¿Qué pasa si necesito hacer un cambio urgente en main?**
R: Tendrás que crear un PR de emergencia y aprobarlo rápidamente.

**P: ¿Puedo cambiar estas reglas después?**
R: Sí, siempre puedes volver a Settings → Branches y modificarlas.

**P: ¿Qué pasa si no tengo cuenta de npm?**
R: Puedes crearla gratis en npmjs.com, es necesaria para publicar el SDK.

**P: ¿Los secrets son seguros?**
R: Sí, GitHub los encripta y solo están disponibles durante la ejecución de Actions.

---

💡 **Tip**: Tómate tu tiempo para hacer cada paso. Es mejor hacerlo bien que rápido.

🎯 **Objetivo final**: Tener un repositorio profesional y seguro que automatice tareas repetitivas.