# Estrategia Móvil

Este proyecto usa React y Vite para la web. Para llegar a iOS y Android, hay dos enfoques principales.

## 1. Frameworks multiplataforma (React Native, Expo)

- **React Native** permite reutilizar gran parte de la lógica en TypeScript/JavaScript.
- **Expo** simplifica la configuración y ofrece herramientas de compilación y publicación.
- Permite acceso nativo (sensores, notificaciones, almacenamiento) con bibliotecas adicionales.
- Desventaja: necesitará adaptar los componentes y estilos de la UI.

## 2. Progressive Web App (PWA)

- Convertir la aplicación web existente en una PWA es un paso intermedio rápido.
- Una PWA se puede instalar en dispositivos móviles y funciona offline mediante caché.
- Brinda una experiencia similar a una app nativa sin depender de tiendas de aplicaciones.
- Sirve para validar funcionalidades móviles antes de invertir en una app nativa.

## Recomendación

1. **Implementar PWA** primero para aprovechar el código web actual. Esto requiere agregar un manifiesto, un service worker y manejar caché/offline.
2. Evaluar **React Native/Expo** para una experiencia más integrada y acceso a funcionalidades nativas. Se puede reutilizar la lógica de negocio y parte de los componentes.
3. Usar lo aprendido en la PWA (navegación, layout adaptable) para guiar el diseño de la app nativa.
