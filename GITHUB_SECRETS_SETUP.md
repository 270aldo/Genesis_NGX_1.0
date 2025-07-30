# 🔐 Configuración de Secretos para GitHub Actions

## Pasos para configurar los secretos

1. **Accede a la configuración de secretos**:
   - Ve a: https://github.com/270aldo/Genesis_NGX_1.0/settings/secrets/actions
   - Haz clic en "New repository secret"

2. **Agrega los siguientes secretos**:

### Secretos Requeridos

| Nombre del Secreto | Descripción | Ejemplo |
|-------------------|-------------|---------|
| `SUPABASE_URL` | URL de tu proyecto Supabase | `https://xxxxx.supabase.co` |
| `SUPABASE_KEY` | Anon key de Supabase | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `VERTEX_AI_PROJECT_ID` | ID del proyecto de Google Cloud | `ngx-genesis-prod` |
| `VERTEX_AI_LOCATION` | Región de Vertex AI | `us-central1` |
| `JWT_SECRET_KEY` | Clave secreta para JWT (genera una nueva) | `your-super-secret-key-here` |
| `ELEVENLABS_API_KEY` | API key de ElevenLabs | `sk_...` |

### Secretos Opcionales

| Nombre del Secreto | Descripción | Ejemplo |
|-------------------|-------------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Credenciales de servicio GCP (JSON completo) | `{"type": "service_account", ...}` |
| `REDIS_URL` | URL de Redis (si usas Redis externo) | `redis://user:pass@host:6379` |
| `SENTRY_DSN` | DSN de Sentry para monitoreo | `https://xxx@sentry.io/xxx` |

## Generación de Claves

### JWT Secret Key
```bash
# Genera una clave segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Google Cloud Service Account
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Navega a IAM & Admin > Service Accounts
3. Crea una cuenta de servicio con permisos de Vertex AI
4. Descarga el JSON y pégalo completo en `GOOGLE_APPLICATION_CREDENTIALS_JSON`

## Verificación

Para verificar que los secretos están configurados:

1. Haz un push a una rama
2. Ve a la pestaña "Actions" en GitHub
3. Revisa los logs de los workflows

Los secretos aparecerán como `***` en los logs por seguridad.

## Troubleshooting

Si los workflows siguen fallando después de configurar los secretos:

1. **Verifica los nombres**: Los nombres deben coincidir exactamente (case-sensitive)
2. **Sin espacios**: Asegúrate de no tener espacios al inicio/final
3. **Formato JSON**: Para `GOOGLE_APPLICATION_CREDENTIALS_JSON`, debe ser JSON válido
4. **Permisos**: La cuenta de servicio debe tener permisos de Vertex AI User

## Seguridad

⚠️ **IMPORTANTE**: 
- Nunca compartas estos secretos
- Rota las claves regularmente
- Usa diferentes claves para desarrollo/staging/producción
- Revoca inmediatamente cualquier clave comprometida