# Translations & multilingual support

## ⚠️ CRITICAL: PrestaShop custom trans() signatures

PrestaShop uses **different parameter order** than standard Symfony translation for `trans()` in form types and controllers.

### In TranslatorAwareType (Form Types)

**Signature:** `trans($key, $domain, $parameters = [])`

```php
// ✅ CORRECT - domain is 2nd parameter
$this->trans('Carousel speed', 'Modules.Mymodule.Admin')
$this->trans('Label with %var%', 'Modules.Mymodule.Admin', ['%var%' => $value])

// ❌ WRONG - will throw "Argument #2 ($parameters) must be of type array, string given"
$this->trans('Carousel speed', [], 'Modules.Mymodule.Admin')
```

**Location:** `PrestaShopBundle\Form\Admin\Type\TranslatorAwareType`

### In FrameworkBundleAdminController (Controllers)

**Signature:** `trans($key, $domain, array $parameters = [])`

```php
// ✅ CORRECT
$this->trans('Successful update.', 'Admin.Notifications.Success')
$this->trans('Item %s saved', 'Modules.Mymodule.Admin', ['%s' => $name])

// ❌ WRONG - will throw "Argument #3 ($parameters) must be of type array, string given"  
$this->trans('Successful update.', [], 'Admin.Notifications.Success')
```

**Location:** `PrestaShopBundle\Controller\Admin\FrameworkBundleAdminController`

### Why this exists

PrestaShop wraps Symfony's `TranslatorInterface` with custom implementations to:
- Support PrestaShop's legacy translation system alongside Symfony's
- Handle module-specific translation domains automatically
- Maintain backward compatibility with older modules

### Standard Symfony (for reference)

Standard Symfony signature (NOT used in PrestaShop forms/controllers):
```php
trans($id, array $parameters = [], $domain = null, $locale = null)
```

### Common mistakes

1. **Using empty array for no parameters:** Always omit the 2nd argument if no parameters needed
2. **Copy-pasting from Symfony docs:** PrestaShop's signature is different
3. **Validation constraint messages in FormType:** Use plain strings, NOT trans() calls:

```php
// ✅ CORRECT - constraint messages as plain strings
new GreaterThanOrEqual([
    'value' => 1000,
    'message' => 'Speed must be at least 1000 milliseconds',
])

// ❌ WRONG - Symfony handles constraint translation separately
new GreaterThanOrEqual([
    'value' => 1000,
    'message' => $this->trans('Speed must be at least...', 'Modules.Mymodule.Admin'),
])
```

---

## Translation domains

PrestaShop uses dot-separated translation domains. The module domain follows the pattern `Modules.{ModuleName}.{Context}`:

```php
// In PHP (controller, module class, service)
$this->trans('Text to translate', [], 'Modules.Mymodule.Admin');
$this->trans('Front text', [], 'Modules.Mymodule.Shop');
```

```twig
{# In Twig templates #}
{{ 'Text to translate'|trans({}, 'Modules.Mymodule.Admin') }}
{{ 'Save'|trans({}, 'Admin.Actions') }}
```

```smarty
{* In Smarty templates *}
{l s='Text to translate' d='Modules.Mymodule.Shop'}
```

## Declaring the new translation system

Add to your main module class:

```php
public function isUsingNewTranslationSystem(): bool
{
    return true;
}
```

## Translation files

### Modern structure (PrestaShop 8+)

PrestaShop 8+ uses ISO code-based folder structure for translation catalogues:

```
translations/
├── fr-FR/
│   └── ModulesMymodule.Admin.fr-FR.xlf
│   └── ModulesMymodule.Shop.fr-FR.xlf
├── en-US/
│   └── ModulesMymodule.Admin.en-US.xlf
│   └── ModulesMymodule.Shop.en-US.xlf
├── de-DE/
│   └── ModulesMymodule.Admin.de-DE.xlf
└── index.php
```

**Key differences from legacy structure:**
- Folders named with full ISO codes (e.g., `fr-FR`, `en-US`, `de-DE`) instead of `default/`
- File naming convention: `Modules{Modulename}.{Context}.{isocode}.xlf`
- Each language has its own folder with properly targeted translations

### Checking and completing XLF translations

XLF files contain `<trans-unit>` elements with `<source>` (original text) and `<target>` (translated text):

```xml
<xliff xmlns="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
  <file original="ModulesMymodule.Admin.xlf" source-language="en-US" target-language="fr-FR" datatype="plaintext">
    <body>
      <trans-unit id="6884a1a593437b739798a6c85b048503">
        <source>Display social wall on your store</source>
        <target>Afficher le mur social sur votre boutique</target>
      </trans-unit>
      <trans-unit id="bc4b8805c947b08122f7cf67c8b7e7a3">
        <source>Please enter a valid URL.</source>
        <target>Veuillez saisir une URL valide.</target>
      </trans-unit>
    </body>
  </file>
</xliff>
```

**Validation steps:**
1. Check that `target-language` attribute matches the ISO code folder name
2. Ensure every `<trans-unit>` has both `<source>` and `<target>` elements
3. Verify that `<target>` contains properly translated text (not just copied from `<source>`)
4. If `<target>` is identical to `<source>`, translate it to the target language

**Common issue:** Auto-generated XLF files often have `<target>` identical to `<source>`:

```xml
<!-- ❌ NOT TRANSLATED -->
<trans-unit id="abc123">
  <source>JavaScript URL</source>
  <target>JavaScript URL</target>  <!-- Should be "URL JavaScript" for French -->
</trans-unit>
```

### Legacy translation files

PrestaShop 1.6/1.7 modules may have legacy translation files at `translations/{isocode}.php`:

```
translations/
├── fr.php      ← Legacy file
├── en.php      ← Legacy file
└── index.php
```

**Migration workflow:**
1. Check if modern ISO code folders exist (e.g., `translations/fr-FR/`)
2. If modern XLF files exist but have untranslated targets, extract translations from legacy `.php` files
3. Legacy `.php` files can be safely deleted once modern XLF files are complete
4. If legacy files are empty (just header/license), delete them immediately

**Example legacy file extraction:**

```php
// translations/fr.php (legacy)
global $_MODULE;
$_MODULE = [];
$_MODULE['<{mymodule}prestashop>mymodule_abc123'] = 'URL JavaScript';
```

Use these values to populate `<target>` in modern XLF files, then delete the legacy `.php` file.

### Generating translation files

Generate modern XLF catalogues with PrestaShop's console command:

```bash
# From PrestaShop root
php bin/console translation:extract --locale=fr-FR --output-format=xlf --module=mymodule
```

This creates XLF files in `translations/{isocode}/` with `<source>` populated. You must manually translate `<target>` values.

## Resources

- [Translation system](https://devdocs.prestashop-project.org/9/development/internationalization/translation/)
