# Validation — mandatory after every change session

> **AI agent rule — NEVER SKIP EITHER STEP**: Both steps below are **mandatory** after every code change session, without exception.
> - Do NOT stop after Step 1 (lotr). Step 2 (install test) is equally required.
> - Do NOT ask the user whether to run them — just run them, every time.
> - Do NOT consider the task complete until both steps pass.

## Step 1 — Dev tools (run from the module root)

```bash
vendor/websenso/prestashop-module-devtools/bin/lotr
```

- Run **without any flags** — applies all fixers in sequence: autoindex, header stamp, PS version checker, PS validator, PHPStan, PHP-CS-Fixer.
- **Working directory must be the module root** (`/path/to/modules/mymodule`), not the PS root.
- Expected output: `🎉 All commands completed successfully!` with `Executed: 6/6 commands successfully`.
- `lotr` may auto-modify files (index.php guards, file headers, CS fixes) — those changes are correct.

**If a step fails**:
1. Read the full error output carefully.
2. Fix all reported errors.
3. Re-run `lotr` until all 6 steps pass.
4. If a PHPStan baseline is needed, document it and report before finalising.

## Step 2 — Module installation test (run from the PS root)

```bash
cd /path/to/prestashop && php bin/console pr:mo install mymodule
```

- **Working directory must be the PS root**, not the module directory.
- Expected output (French PS): `L'action Install sur le module … a réussi.`
- Expected output (English PS): `Action Install on module … succeeded.`

**If install fails — common causes**:

| Error | Fix |
|---|---|
| `Attempted to load class …` | Missing `require_once __DIR__ . '/vendor/autoload.php';` in main module file |
| `Call to undefined method` | Wrong namespace or missing `use` statement |
| DB errors | Review `ConfigurationInstaller` and SQL queries in `Installer` |
| `Class "…OldController" cannot be found` (DI compile error) | Old class name still registered in `config/services.yml` — update it to the new class name |
| `Cannot declare class … because the name is already in use` | Old PHP file still on disk after a rename — delete the old file |

> **After any controller rename**: update both the PHP filename AND the service entry in `config/services.yml`. Both must match the new class name.

If the module was already installed: `php bin/console pr:mo uninstall mymodule`, then re-install.

After a successful install, clear cache if routes are not resolving: `php bin/console cache:clear`.
