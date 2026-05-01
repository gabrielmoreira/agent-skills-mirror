# Modern configuration page

> **⚠️ DO NOT use `HelperForm`** — it is based on Smarty + Bootstrap 3 and is explicitly discouraged in Symfony controllers. See https://devdocs.prestashop-project.org/9/development/components/helpers/helperform/
> **⚠️ DO NOT use `getContent()` to render HTML** — only use it to redirect to the Symfony route.

> **⚠️ CRITICAL:** PrestaShop's `trans()` uses **different parameter order** than Symfony. See **[translations.md](translations.md#-critical-prestashop-custom-trans-signatures)** for correct signatures in `TranslatorAwareType` (forms) and `FrameworkBundleAdminController` (controllers).

The canonical pattern uses four classes and two config files:

```
config/routes.yml                           # declares the Symfony route
config/services.yml                         # wires all services + controller
src/Form/ConfigurationDataConfiguration.php # reads/writes PS configuration table
src/Form/ConfigurationFormDataProvider.php  # bridges form ↔ DataConfiguration
src/Form/ConfigurationFormType.php          # Symfony form type (no HelperForm!)
src/Controller/Admin/ConfigurationController.php  # handles GET/POST, renders Twig
views/templates/admin/configuration.html.twig     # Twig template with PS UI Kit
```

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

## `config/services.yml`

```yaml
services:
  _defaults:
    public: true

  prestashop.module.mymodule.form.configuration_data_configuration:
    class: Vendor\MyModule\Form\ConfigurationDataConfiguration
    arguments:
      - '@prestashop.adapter.legacy.configuration'

  prestashop.module.mymodule.form.configuration_data_provider:
    class: Vendor\MyModule\Form\ConfigurationFormDataProvider
    arguments:
      - '@prestashop.module.mymodule.form.configuration_data_configuration'

  prestashop.module.mymodule.form.type.configuration:
    class: Vendor\MyModule\Form\ConfigurationFormType
    parent: 'form.type.translatable.aware'
    tags:
      - { name: form.type }

  prestashop.module.mymodule.form.configuration_data_handler:
    class: PrestaShop\PrestaShop\Core\Form\Handler
    arguments:
      - '@form.factory'
      - '@prestashop.core.hook.dispatcher'
      - '@prestashop.module.mymodule.form.configuration_data_provider'
      - 'Vendor\MyModule\Form\ConfigurationFormType'
      - 'MymoduleConfiguration'

  Vendor\MyModule\Controller\Admin\ConfigurationController:
    public: true
    arguments:
      - '@prestashop.module.mymodule.form.configuration_data_handler'
      - '@prestashop.adapter.legacy.configuration'
    tags:
      - { name: controller.service_arguments }
```

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

```php
class ConfigurationController extends FrameworkBundleAdminController
{
    public function __construct(
        private FormHandlerInterface $formHandler,
        private ConfigurationInterface $configuration
    ) {}

    public function index(Request $request): Response
    {
        $form = $this->formHandler->getForm();
        $form->handleRequest($request);

        if ($form->isSubmitted() && $form->isValid()) {
            $errors = $this->formHandler->save($form->getData());
            if (empty($errors)) {
                $this->addFlash('success', $this->trans('Successful update.', 'Admin.Notifications.Success'));
                return $this->redirectToRoute('mymodule_configuration');
            }
            foreach ($errors as $error) { $this->addFlash('danger', $error); }
        }

        return $this->render(
            '@Modules/mymodule/views/templates/admin/configuration.html.twig',
            ['configurationForm' => $form->createView()]
        );
    }
}
```

## `views/templates/admin/configuration.html.twig`

```twig
{% form_theme configurationForm '@PrestaShop/Admin/TwigTemplateForm/prestashop_ui_kit.html.twig' %}
{% extends '@PrestaShop/Admin/layout.html.twig' %}
{% block content %}
  {{ form_start(configurationForm) }}
  <div class="card">
    <h3 class="card-header"><i class="material-icons">settings</i> {{ 'Settings'|trans({}, 'Admin.Global') }}</h3>
    <div class="card-body"><div class="form-wrapper">{{ form_widget(configurationForm) }}</div></div>
    <div class="card-footer"><div class="d-flex justify-content-end">
      <button type="submit" class="btn btn-primary">{{ 'Save'|trans({}, 'Admin.Actions') }}</button>
    </div></div>
  </div>
  {{ form_end(configurationForm) }}
{% endblock %}
```

## Reference implementation

[demosymfonyform](https://github.com/PrestaShop/example-modules/tree/master/demosymfonyform) — canonical official example

---

> **Form field rules** (apply to all forms, not just configuration): see **[forms.md](forms.md)**.
