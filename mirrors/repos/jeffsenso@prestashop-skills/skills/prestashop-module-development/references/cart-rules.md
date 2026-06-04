# PrestaShop Cart Rules (Vouchers)

## Overview

PrestaShop's `CartRule` class (`/classes/CartRule.php`) manages discount vouchers and promotional codes. Cart rules can offer percentage discounts, fixed amount discounts, free shipping, or free gifts.

## Creating Cart Rules Programmatically

### Basic Cart Rule Creation

```php
use CartRule;
use DateTime;
use Language;

$cartRule = new CartRule();

// Name (multilang field - required for all languages)
$languages = Language::getLanguages(true);
foreach ($languages as $language) {
    $cartRule->name[(int) $language['id_lang']] = 'My Cart Rule Name';
}

// Code (optional - if empty, cart rule applies automatically)
$cartRule->code = 'MYCODE2024';

// Dates (required)
$now = new DateTime();
$cartRule->date_from = $now->format('Y-m-d H:i:s');
$cartRule->date_to = $now->modify('+30 days')->format('Y-m-d H:i:s');

// Active state
$cartRule->active = true;

// Save
$cartRule->add();
```

## Voucher Code Generation

### PrestaShop's Official Character Set

PrestaShop uses a specific character set for voucher codes to avoid confusion:

```php
// Character set (no O or 0 to avoid confusion)
$chars = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ';

function generateCode(int $length = 8): string
{
    $chars = '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ';
    $charsLength = strlen($chars);
    $code = '';
    
    for ($i = 0; $i < $length; ++$i) {
        $code .= $chars[random_int(0, $charsLength - 1)];
    }
    
    return $code;
}
```

### Ensuring Uniqueness

```php
function generateUniqueCode(int $length = 8, int $maxAttempts = 10): string
{
    $attempt = 0;
    
    do {
        $code = generateCode($length);
        $exists = CartRule::getIdByCode($code);
        ++$attempt;
    } while ($exists && $attempt < $maxAttempts);
    
    if ($exists) {
        throw new \RuntimeException('Could not generate unique code');
    }
    
    return $code;
}
```

**Reference**: PrestaShop admin UI uses the same character set in `/js/admin.js` - `gencode()` function.

## Cart Rule Properties

### Essential Fields

```php
// Multilang name (required)
$cartRule->name = [
    1 => 'English Name',
    2 => 'French Name',
];

// Code (8 characters recommended)
$cartRule->code = 'ABC12345';

// Dates (both required)
$cartRule->date_from = '2024-01-01 00:00:00';
$cartRule->date_to = '2024-12-31 23:59:59';

// Active state
$cartRule->active = true; // or false
```

### Reduction Types

**Percentage discount:**
```php
$cartRule->reduction_percent = 10.0; // 10% discount
$cartRule->reduction_tax = true; // Include tax in calculation
```

**Fixed amount discount:**
```php
$cartRule->reduction_amount = 15.0; // €15 discount
$cartRule->reduction_currency = 1; // Currency ID
$cartRule->reduction_tax = true; // Include tax
```

**Free shipping:**
```php
$cartRule->free_shipping = true;
```

**Free gift:**
```php
$cartRule->gift_product = 123; // Product ID
$cartRule->gift_product_attribute = 0; // Combination ID (0 = no combination)
```

### Quantity Settings

```php
// Total quantity available
$cartRule->quantity = 100;

// Quantity per user
$cartRule->quantity_per_user = 1;

// Priority (lower = higher priority)
$cartRule->priority = 1;
```

### Usage Options

```php
// Highlight in back office
$cartRule->highlight = true;

// Allow partial use (for amount-based discounts)
$cartRule->partial_use = true;
```

### Customer Restrictions

```php
// Restrict to specific customer
$cartRule->id_customer = 12345;

// OR restrict to customer groups
$cartRule->group_restriction = true;
// Then add groups via CartRule::addGroup() after save
```

### Cart Conditions

```php
// Minimum cart amount
$cartRule->minimum_amount = 50.0;
$cartRule->minimum_amount_tax = true; // Include tax
$cartRule->minimum_amount_currency = 1; // Currency ID
$cartRule->minimum_amount_shipping = false; // Include shipping in total
```

### Restriction Flags

All restriction flags default to `false` (no restriction):

```php
// Country restriction
$cartRule->country_restriction = false;

// Carrier restriction
$cartRule->carrier_restriction = false;

// Group restriction
$cartRule->group_restriction = false;

// Cart rule compatibility restriction
$cartRule->cart_rule_restriction = false;

// Product restriction
$cartRule->product_restriction = false;

// Shop restriction (multishop)
$cartRule->shop_restriction = false;
```

When set to `true`, you must configure the specific restrictions after saving the cart rule.

## Complete Example: Customer-Specific Voucher

```php
use CartRule;
use Configuration;
use DateTime;
use Language;

function createCustomerVoucher(
    int $customerId,
    string $firstname,
    string $lastname,
    float $reductionPercent,
    int $durationDays
): CartRule {
    $cartRule = new CartRule();
    
    // Multilang name
    $name = sprintf('Auto Reduction %.0f%% - %s %s', $reductionPercent, $firstname, $lastname);
    $languages = Language::getLanguages(true);
    foreach ($languages as $language) {
        $cartRule->name[(int) $language['id_lang']] = $name;
    }
    
    // Generate unique code
    $cartRule->code = generateUniqueCode(8);
    
    // Dates
    $now = new DateTime();
    $cartRule->date_from = $now->format('Y-m-d H:i:s');
    $cartRule->date_to = $now->modify(sprintf('+%d days', $durationDays))->format('Y-m-d H:i:s');
    
    // Customer restriction
    $cartRule->id_customer = $customerId;
    
    // Reduction
    $cartRule->reduction_percent = $reductionPercent;
    $cartRule->reduction_tax = true;
    
    // Options
    $cartRule->highlight = true;
    $cartRule->partial_use = true;
    $cartRule->active = true;
    
    // Quantities
    $cartRule->quantity = 1;
    $cartRule->quantity_per_user = 1;
    $cartRule->priority = 1;
    
    // No other restrictions
    $cartRule->country_restriction = false;
    $cartRule->carrier_restriction = false;
    $cartRule->group_restriction = false;
    $cartRule->cart_rule_restriction = false;
    $cartRule->product_restriction = false;
    $cartRule->shop_restriction = false;
    
    // No other discounts
    $cartRule->free_shipping = false;
    $cartRule->reduction_amount = 0;
    $cartRule->reduction_currency = 0;
    $cartRule->reduction_product = 0;
    $cartRule->gift_product = 0;
    $cartRule->gift_product_attribute = 0;
    
    // No minimum amount
    $cartRule->minimum_amount = 0;
    $cartRule->minimum_amount_tax = false;
    $cartRule->minimum_amount_currency = 0;
    $cartRule->minimum_amount_shipping = false;
    
    // Save
    $cartRule->add();
    
    return $cartRule;
}
```

## CartRule Methods

### Checking Existence

```php
// Check if code exists
$idCartRule = CartRule::getIdByCode('MYCODE');
if ($idCartRule) {
    // Code already exists
}

// Check if customer already used a cart rule
$cartRule = new CartRule($id);
$used = $cartRule->usedByCustomer($customerId);
```

### Getting Cart Rules

```php
// Get cart rules for a customer
$cartRules = CartRule::getCustomerCartRules(
    $languageId,
    $customerId,
    $active = true,
    $includeGeneric = true,
    $inStock = true,
    Cart $cart = null,
    $freeShippingOnly = false,
    $highlight = false
);
```

## Field Validation

PrestaShop's CartRule class validates:

- **name**: Required multilang field
- **date_from** and **date_to**: Required, must be valid dates
- **code**: Optional, max 254 characters, cleaned HTML
- **reduction_percent**: Must be between 0 and 100
- **reduction_amount**: Must be >= 0
- **quantity**: Must be unsigned int
- **id_customer**: Must be valid customer ID or 0

## Common Patterns

### Auto-Apply Cart Rule (No Code)

```php
$cartRule->code = ''; // Empty code = auto-apply
$cartRule->group_restriction = true; // Restrict to specific group
// Add groups after save
```

### Limited-Time Flash Sale

```php
$cartRule->highlight = true; // Highlight in back office
$cartRule->date_to = (new DateTime())->modify('+24 hours')->format('Y-m-d H:i:s');
$cartRule->quantity = 100; // Limited quantity
```

### First Order Discount

```php
$cartRule->quantity_per_user = 1; // One use per customer
$cartRule->minimum_amount = 0; // No minimum
// Check customer order count before applying
```

## Best Practices

1. **Always generate unique codes** - Use `CartRule::getIdByCode()` to check before creating
2. **Use PrestaShop's character set** - Avoid O/0 confusion with `123456789ABCDEFGHIJKLMNPQRSTUVWXYZ`
3. **Set multilang names** - Required for all active languages
4. **Set appropriate dates** - Always include time (H:i:s), not just date
5. **Test cart rule application** - Use PrestaShop's cart simulator before deploying
6. **Set priority correctly** - Lower numbers = higher priority when multiple rules apply
7. **Use highlight flag** - Makes cart rules easy to find in back office
8. **Consider partial_use** - For amount-based discounts that can be used multiple times

## Reference

- CartRule class: `/classes/CartRule.php`
- Admin controller: `/controllers/admin/AdminCartRulesController.php`
- Code generation: `/js/admin.js` - `gencode()` function
- Front display: `/classes/Cart.php` - cart rule application logic
