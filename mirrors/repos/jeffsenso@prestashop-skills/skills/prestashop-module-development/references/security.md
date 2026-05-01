# Security implementation

Always implement these security measures in every admin form or AJAX endpoint.

## CSRF token validation

In Symfony controllers, CSRF is handled automatically by the framework when forms use `form.factory`. For manual AJAX endpoints, validate the token explicitly:

```php
if (!$this->isCsrfTokenValid('my_action', $request->request->get('_token'))) {
    throw $this->createAccessDeniedException('Invalid CSRF token.');
}
```

In legacy controllers:
```php
if (!Tools::getToken(false)) {
    $this->context->controller->errors[] = $this->trans('Invalid token', [], 'Admin.Notifications.Error');
    return false;
}
```

## Input validation and sanitization

```php
$input = Tools::getValue('input_field');
if (!Validate::isGenericName($input)) {
    $this->context->controller->errors[] = $this->trans('Invalid input', [], 'Admin.Notifications.Error');
    return false;
}
```

Common `Validate::` methods: `isGenericName`, `isInt`, `isBool`, `isEmail`, `isUrl`, `isHtml`, `isUnsignedInt`.

## SQL injection prevention

Always cast numeric values and escape strings:

```php
// Cast IDs
$sql = 'SELECT * FROM ' . _DB_PREFIX_ . 'my_table WHERE id = ' . (int) $id;

// Escape strings
$sql = 'SELECT * FROM ' . _DB_PREFIX_ . 'my_table WHERE name = "' . pSQL($name) . '"';

// DbQuery builder (preferred)
$sql = new DbQuery();
$sql->select('*')
    ->from('my_table')
    ->where('id = ' . (int) $id);
$result = Db::getInstance(_PS_USE_SQL_SLAVE_)->executeS($sql);
```

Never interpolate unvalidated request input directly into SQL strings.

## Admin access control

```php
if (!$this->context->employee->hasAccess($this->id, 'edit')) {
    throw new PrestaShopException('Access denied');
}
```

In Symfony controllers, use `$this->denyAccessUnlessGranted()` or rely on `_legacy_controller` permission checking built into `FrameworkBundleAdminController`.

## File upload security

Always use `ImageManager::validateUpload()` and provide the full `$_FILES`-compatible array including `name`, `tmp_name`, `type`, `size`, `error`:

```php
$fileData = [
    'name'     => $_FILES['photo']['name'],
    'tmp_name' => $_FILES['photo']['tmp_name'],
    'type'     => mime_content_type($_FILES['photo']['tmp_name']) ?: 'application/octet-stream',
    'size'     => $_FILES['photo']['size'],
    'error'    => $_FILES['photo']['error'],
];
$uploadError = ImageManager::validateUpload($fileData, Tools::getMaxUploadSize());
if ($uploadError) {
    // handle error
}
```
