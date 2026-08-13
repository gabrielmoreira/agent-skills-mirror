# Modern configuration page

> **⚠️ DO NOT use `HelperForm`** — it is based on Smarty + Bootstrap 3 and is explicitly discouraged in Symfony controllers. See https://devdocs.prestashop-project.org/9/development/components/helpers/helperform/
> **⚠️ DO NOT use `getContent()` to render HTML** — only use it to redirect to the Symfony route.
> **⚠️ DO NOT access services via `$this->get()` in controllers** — Controllers have a limited service locator. Use constructor dependency injection instead. See the **FormHandler pattern** below.

> **⚠️ CRITICAL:** PrestaShop's `trans()` uses **different parameter order** than Symfony. See **[translations.md](translations.md#-critical-prestashop-custom-trans-signatures)** for correct signatures in `TranslatorAwareType` (forms) and `FrameworkBundleAdminController` (controllers).

## **MANDATORY: Use FormHandler with dependency injection**

The canonical pattern uses **four classes** (DataConfiguration, FormDataProvider, FormType, Controller), **one FormHandler service**, and **dependency injection** in the controller:

```
config/routes.yml                           # declares the Symfony route
config/components/configuration/services.yml # wires all services + controller
src/Form/Configuration/DataConfiguration.php # reads/writes PS configuration table
src/Form/Configuration/FormDataProvider.php  # bridges form ↔ DataConfiguration
src/Form/Configuration/FormType.php          # Symfony form type (no HelperForm!)
src/Controller/Admin/ConfigurationController.php  # handles GET/POST, renders Twig
views/templates/admin/configuration.html.twig     # Twig template with PS UI Kit
```

### **Why FormHandler + dependency injection?**

**❌ PROBLEM**: Controllers in PrestaShop have a **limited service locator** that only knows about a small set of services:

```
Service "mymodule.form.configuration_data_provider" not found: even though it exists 
in the app's container, the container inside "Vendor\MyModule\Controller\Admin\ConfigurationController" 
is a smaller service locator that only knows about the "form.factory", "http_kernel", 
"parameter_bag", "request_stack", "router", "security.authorization_checker", 
"security.csrf.token_manager", "security.token_storage", "serializer", "twig" 
and "web_link.http_header_serializer" services.
```

**✅ SOLUTION**: Use **constructor dependency injection** + **FormHandler**:
- FormHandler wraps the complete form workflow (creation, validation, saving)
- Controller receives FormHandler via constructor (not `$this->get()`)
- Controller is registered as a **public service** with explicit `controller.service_arguments` tag

## `config/routes.yml`

```yaml
mymodule_configuration:
  path: /mymodule/configuration
  methods: [GET, POST]
  defaults:
    _controller: 'Vendor\MyModule\Controller\Admin\ConfigurationController::index'
    _legacy_controller: AdminMymoduleConfiguration
    _legacy_link: AdminMymoduleConfiguration
```

## `config/components/configuration/services.yml`

**CRITICAL**: Register all services including the controller, and use the FormHandler pattern:

```yaml
services:
  # --- Data configuration (reads/writes PS configuration table) ---
  prestashop.module.mymodule.form.configuration_data_configuration:
    class: Vendor\MyModule\Form\Configuration\DataConfiguration
    arguments:
      - '@prestashop.adapter.legacy.configuration'

  # --- Form data provider (bridges form ↔ data configuration) ---
  prestashop.module.mymodule.form.configuration_data_provider:
    class: Vendor\MyModule\Form\Configuration\FormDataProvider
    arguments:
      - '@prestashop.module.mymodule.form.configuration_data_configuration'

  # --- Symfony form type (with parent and tags) ---
  prestashop.module.mymodule.form.type.configuration:
    class: Vendor\MyModule\Form\Configuration\FormType
    parent: 'form.type.translatable.aware'
    tags:
      - { name: form.type }

  # --- Form handler (wraps the complete workflow) ---
  prestashop.module.mymodule.form.configuration_data_handler:
    class: PrestaShop\PrestaShop\Core\Form\Handler
    arguments:
      - '@form.factory'
      - '@prestashop.core.hook.dispatcher'
      - '@prestashop.module.mymodule.form.configuration_data_provider'
      - 'Vendor\MyModule\Form\Configuration\FormType'
      - 'MymoduleConfiguration'  # Hook name prefix

  # --- Admin controller (PUBLIC with dependency injection) ---
  Vendor\MyModule\Controller\Admin\ConfigurationController:
    public: true
    arguments:
      - '@prestashop.module.mymodule.form.configuration_data_handler'
    tags:
      - { name: controller.service_arguments }
```

**Key points**:
- FormType must have `parent: 'form.type.translatable.aware'` and `tags: [{ name: form.type }]`
- FormHandler class is **PrestaShop's Core `PrestaShop\PrestaShop\Core\Form\Handler`**
- Controller must be **`public: true`** with **`controller.service_arguments` tag**
- Controller receives FormHandler via constructor, **NOT via `$this->get()`**

## `src/Form/ConfigurationDataConfiguration.php`

> **⚠️ IntegerType fields:** If your form has integer fields, return `0` (int) not `''` (string) from `getConfiguration()` to avoid "Expected a numeric" errors. See [forms.md](forms.md#%EF%B8%8F-integertype-with-optionalempty-values).

```php
final class ConfigurationDataConfiguration implements DataConfigurationInterface
{
    public const CONFIG_TITLE = 'MYMODULE_TITLE';

    public function __construct(private ConfigurationInterface $configuration) {}

    public function getConfiguration(): array
    {
        return ['title' => $this->configuration->get(self::CONFIG_TITLE) ?? ''];
    }

    public function updateConfiguration(array $configuration): array
    {
        $this->configuration->set(self::CONFIG_TITLE, $configuration['title'] ?? '');
        return [];
    }

    public function validateConfiguration(array $configuration): bool { return true; }
}
```

## `src/Form/ConfigurationFormType.php`

> **Note:** `trans($key, $domain)` — domain is 2nd parameter, NOT 3rd. See [translations.md](translations.md#-critical-prestashop-custom-trans-signatures).

```php
class ConfigurationFormType extends TranslatorAwareType
{
    public function buildForm(FormBuilderInterface $builder, array $options): void
    {
        $builder->add('title', TextType::class, [
            'label' => $this->trans('Title', 'Modules.Mymodule.Admin'),
            'required' => false,
        ]);
    }

    public function configureOptions(OptionsResolver $resolver): void
    {
        parent::configureOptions($resolver);
        $resolver->setDefaults([
            'form_theme' => '@PrestaShop/Admin/TwigTemplateForm/prestashop_ui_kit.html.twig',
        ]);
    }
}
```

## `src/Controller/Admin/ConfigurationController.php`

**MANDATORY: Use constructor dependency injection with FormHandler**:

```php
<?php

declare(strict_types=1);

namespace Vendor\MyModule\Controller\Admin;

use PrestaShop\PrestaShop\Core\Form\FormHandlerInterface;
use PrestaShopBundle\Controller\Admin\FrameworkBundleAdminController;
use PrestaShopBundle\Security\Annotation\AdminSecurity;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class ConfigurationController extends FrameworkBundleAdminController
{
    private FormHandlerInterface $formHandler;

    public function __construct(FormHandlerInterface $formHandler)
    {
        $this->formHandler = $formHandler;
    }

    /**
     * @AdminSecurity("is_granted('read', request.get('_legacy_controller'))")
     */
    public function indexAction(Request $request): Response
    {
        $form = $this->formHandler->getForm();
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $errors = $this->formHandler->save($form->getData());

            if (empty($errors)) {
                $this->addFlash('success', $this->trans('Successful update', 'Admin.Notifications.Success'));

                return $this->redirectToRoute('mymodule_configuration');
            }

            foreach ($errors as $error) {
                $this->addFlash('error', $error);
            }
        }

        return $this->render(
            '@Modules/mymodule/views/templates/admin/configuration.html.twig',
            [
                'configurationForm' => $form->createView(),
                'layoutHeaderToolbarBtn' => [],
                'layoutTitle' => $this->trans('Configuration', 'Modules.Mymodule.Admin'),
                'requireBulkActions' => false,
                'showContentHeader' => true,
                'enableSidebar' => true,
                'help_link' => false,
            ]
        );
    }
}
```

**❌ WRONG — DO NOT DO THIS**:
```php
// ❌ WRONG: Trying to get service from limited service locator
$formDataProvider = $this->get('mymodule.form.configuration_data_provider');
// This will fail with "Service not found" error
```

**✅ CORRECT — USE THIS**:
```php
// ✅ CORRECT: Inject FormHandler via constructor
private FormHandlerInterface $formHandler;

public function __construct(FormHandlerInterface $formHandler)
{
    $this->formHandler = $formHandler;
}

// Then use it:
$form = $this->formHandler->getForm();
$errors = $this->formHandler->save($form->getData());
```

## `views/templates/admin/configuration.html.twig`

**CRITICAL**: Always use the PrestaShop UI Kit form theme and **wrap the form correctly**:

```twig
{% form_theme configurationForm '@PrestaShop/Admin/TwigTemplateForm/prestashop_ui_kit.html.twig' %}
{% extends '@PrestaShop/Admin/layout.html.twig' %}

{% block content %}
  <div class="row justify-content-center">
    <div class="col-lg-8">
      {{ form_start(configurationForm) }}
      <div class="card">
        <h3 class="card-header">
          <i class="material-icons">settings</i>
          {{ 'Configuration'|trans({}, 'Admin.Global') }}
        </h3>
        <div class="card-body">
          {{ form_widget(configurationForm) }}
        </div>
        <div class="card-footer">
          <button type="submit" class="btn btn-primary float-right">
            <i class="material-icons">save</i>
            {{ 'Save'|trans({}, 'Admin.Actions') }}
          </button>
        </div>
      </div>
      {{ form_end(configurationForm) }}
    </div>
  </div>
{% endblock %}
```

**Key points**:
- **`form_theme` directive must be FIRST**, before `extends`
- **`form_start()` must wrap the entire card** — place it BEFORE `<div class="card">`
- **`form_end()` must be AFTER the closing `</div>` of the card**
- **`card-footer` must be a sibling of `card-body`**, not nested inside it
- This structure ensures proper HTML form tags and prevents broken layouts

## Reference implementation

[demosymfonyform](https://github.com/PrestaShop/example-modules/tree/master/demosymfonyform) — canonical official example

---

> **Form field rules** (apply to all forms, not just configuration): see **[forms.md](forms.md)**.
>
> **Per-language fields** (`TranslatableType`): full pattern including the required locale-switcher JS bundle, per-lang storage in `DataConfiguration`, and the `{% block javascripts %}` Twig block: see **[forms.md — TranslatableType section](forms.md#translatabletype--per-language-fields)**.
