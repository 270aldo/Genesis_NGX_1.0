# Desktop Packaging Evaluation

This document summarises how to package the existing React + Vite application for desktop.

## Options

### Electron
- **Pros**
  - Mature ecosystem and extensive documentation.
  - Allows access to Node.js APIs directly in the main process.
- **Cons**
  - Large binary size (>100MB for basic apps).
  - Higher memory usage and slower startup time.

### Tauri
- **Pros**
  - Very small binary size (few MB) as it uses the system webview.
  - Written in Rust with strong security defaults.
  - Cross‑platform (macOS, Windows, Linux).
- **Cons**
  - Requires Rust toolchain for development.
  - Some Node.js APIs require bridges or plugins.

## Recommended Approach

Tauri is the preferred choice for this project due to the smaller footprint and tight integration with Vite. A simple setup can be achieved with the `@tauri-apps/cli` package.

### Setup Steps

1. Install the Tauri CLI:
   ```sh
   npm add -D @tauri-apps/cli
   ```
2. Initialise Tauri in the project root:
   ```sh
   npx tauri init
   ```
   This generates the `src-tauri` directory with configuration files.
3. Run the desktop app in development mode:
   ```sh
   npm run tauri dev
   ```
4. Build distributable binaries:
   ```sh
   npm run tauri build
   ```

For Electron, the typical workflow would require adding `electron` and related tooling (e.g. `electron-builder`) and wiring the Vite build output into an Electron main process.

## Responsive Layout & Keyboard Shortcuts

- The application already uses Tailwind CSS with responsive utility classes. The layout adapts from small to large screens, so it behaves well when the desktop window is resized.
- Keyboard shortcuts are handled via the `useKeyboardShortcuts` hook, which attaches listeners to `document`. This works in both a browser and the desktop webview.

No additional changes are required for these features to function inside a desktop window.
