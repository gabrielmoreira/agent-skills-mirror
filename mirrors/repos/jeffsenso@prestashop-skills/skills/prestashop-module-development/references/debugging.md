# Debugging & failure modes

## Module installation issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Attempted to load class … Did you forget a use statement?` | Missing `require_once __DIR__ . '/vendor/autoload.php';` | Add it right after the `_PS_VERSION_` guard |
| `Call to undefined method` | Wrong namespace / missing `use` | Check namespace in `composer.json` and class files |
| DB error during install | Bad SQL in `Installer` or `ConfigurationInstaller` | Review `install()` SQL, ensure tables don't already exist |
| Hook not triggered | Hook not registered in `Installer` | Add to `$hooks` array, run `pr:mo install` again |

## Configuration page problems

| Symptom | Likely cause | Fix |
|---|---|---|
| Blank page / 500 on config route | Missing service definition | Check `config/services.yml`, run `cache:clear` |
| Form not saving | `DataConfiguration::updateConfiguration()` has a bug | Add error logging; check `validateConfiguration()` |
| Redirect loop | `getContent()` returning HTML instead of redirecting | Use `Tools::redirectAdmin($router->generate(...))` |
| "Unknown filter string" Twig error | `\|string` does not exist in Twig | Use `~ ''` string concatenation trick instead |

## Form field issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Expected a numeric` on `IntegerType` | Empty string from database or empty field | See [forms.md](forms.md#%EF%B8%8F-integertype-with-optionalempty-values) — use `0` instead of `''` |
| `Argument #2 must be of type array, string given` in FormType | Wrong `trans()` signature | Use `trans($key, $domain)` NOT `trans($key, [], $domain)` — see [translations.md](translations.md#%EF%B8%8F-critical-prestashop-custom-trans-signatures) |
| `Argument #3 must be of type array, string given` in Controller | Wrong `trans()` signature | Use `trans($key, $domain, [])` with empty array as 3rd param — see [translations.md](translations.md#%EF%B8%8F-critical-prestashop-custom-trans-signatures) |
| Boolean toggle renders as plain radio | Using `RadioType` instead of `SwitchType` | Use `SwitchType` — see [forms.md](forms.md#boolean--toggle-fields--always-use-switchtype-never-radiotype) |
| Constraint validation message not translated | Using `trans()` in constraint message | Use plain string in constraint; Symfony handles translation separately |

## Grid system issues

| Symptom | Likely cause | Fix |
|---|---|---|
| "Service not found" on Grid factory | Service not defined in `services.yml` | Add all 5 Grid services (factory, query, data, grid, position) |
| Toggle AJAX fails | Route param mismatch | `route_param_name` in `ToggleColumn` must match controller param name exactly |
| Drag-and-drop not working | Bundle JS not loaded or wrong grid ID | Check `wsfaq.bundle.js` is added in header hook; verify grid ID in bundle |
| PHPStan: `getFilters()` return type | Returning concrete `FilterCollection` | Change return type to `FilterCollectionInterface` |
| PHPStan: `getGridActions()` return type | Returning concrete `GridActionCollection` | Change return type to `GridActionCollectionInterface` |

## InputBag issues (Symfony HTTP Foundation)

| Symptom | Likely cause | Fix |
|---|---|---|
| `Unexpected value for parameter … default must be scalar` | `$request->request->get('key', [])` — non-scalar default | Use `$request->request->all()` (no argument), then extract key manually |
| `Unexpected value for parameter` with `all('key')` | Value is not actually an array | Use `$request->request->all()` with no key, then `$data['key'] ?? null` |

## ImageManager::validateUpload issues

Pass the full `$_FILES`-compatible array including `type`, `size`, `error` — not just `tmp_name` and `name`:

```php
$fileData = [
    'name'     => $_FILES['photo']['name'],
    'tmp_name' => $_FILES['photo']['tmp_name'],
    'type'     => mime_content_type($_FILES['photo']['tmp_name']) ?: 'application/octet-stream',
    'size'     => $_FILES['photo']['size'],
    'error'    => $_FILES['photo']['error'],
];
```

## Performance problems

- Avoid loading CSS/JS on every back-office page — check `Tools::getValue('controller')` first.
- Use `_PS_USE_SQL_SLAVE_` for SELECT queries.
- Use `$this->isCached()` pattern for widget templates.
- Avoid N+1 queries in loops — fetch related data in bulk.

## lotr step failures

| lotr step | Common failure | Fix |
|---|---|---|
| autoindex | Missing `index.php` in a subdirectory | lotr auto-adds them; re-run |
| PS validator | Copyright year mismatch (2007-2019 vs 2007-2026) | `sed -i 's/2007-2019/2007-2026/g' views/js/myfile.bundle.js` |
| PHPStan | Return type errors, missing `use` imports | Fix reported types, add missing imports |
| PHP-CS-Fixer | Code style violations | lotr auto-fixes most; review diffs |
