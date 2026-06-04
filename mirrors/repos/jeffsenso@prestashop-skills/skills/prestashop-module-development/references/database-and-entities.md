# Database operations & entities

## Modern approach — Doctrine entities

For entities managed via the Grid system, or any entity with translatable fields, always use the full **Doctrine ORM + Repository + Manager + MetadataListener** pattern.

**Read `references/entity-doctrine.md` for the complete implementation.**

Summary of the pattern:
- `src/Entity/MyEntity.php` — `@ORM\Entity` with `@ORM\HasLifecycleCallbacks`
- `src/Entity/MyEntityLang.php` — translatable fields, `@ORM\ManyToOne` to main entity + `PrestaShopBundle\Entity\Lang`
- `src/Repository/MyEntityRepository.php` — extends `EntityRepository`, handles persist/remove/DBAL queries
- `src/Manager/MyEntityManager.php` — receives Repository + LangRepository via DI, owns the upsert logic
- `src/Doctrine/EventListener/MetadataListener.php` — sets `_DB_PREFIX_` table names at runtime
- `config/common.yml` — wires repository (via factory) + MetadataListener tag



```php
class MyEntityObjectModel extends ObjectModel
{
    public $id;
    public static $definition = [
        'table' => 'my_entity',
        'primary' => 'id',
        'fields' => [
            'name' => ['type' => self::TYPE_STRING, 'validate' => 'isGenericName'],
        ],
    ];
}
```

ObjectModel remains acceptable for simple cases (no joins, no repository), but prefer Doctrine for anything queried via the Grid system.

## Raw SQL with Db (legacy fallback)

Use only when Doctrine is not appropriate:

```php
// SELECT (read replica)
$rows = Db::getInstance(_PS_USE_SQL_SLAVE_)->executeS('
    SELECT *
    FROM ' . _DB_PREFIX_ . 'my_table
    WHERE id_shop = ' . (int) $idShop
);

// INSERT / UPDATE / DELETE (master)
Db::getInstance()->execute('
    INSERT INTO ' . _DB_PREFIX_ . 'my_table (name) VALUES ("' . pSQL($name) . '")'
);
```

Always cast IDs to `(int)` and wrap strings with `pSQL()`.

## Querying PrestaShop core orders — the "logable" pattern

**CRITICAL**: When querying PrestaShop's `orders` table for statistics, reports, or customer eligibility, always use the **`os.logable = 1` pattern** from `AdminStatsController`.

### Why use `logable`?

PrestaShop's order states have a `logable` flag that determines whether an order should be counted in statistics. This is the official pattern used by:
- Dashboard statistics (`AdminStatsController::getOrders()`)
- Sales reports (`AdminStatsController::getTotalSales()`)
- All core PrestaShop analytics

**Logable states** typically include:
- Payment accepted
- Processing in progress
- Shipped
- Delivered

**Non-logable states** (excluded from statistics):
- Payment pending
- Cancelled
- Refunded
- Error/awaiting payment

### DBAL query pattern (modern)

```php
// ✅ CORRECT — uses logable flag, matches PrestaShop core statistics
$qb = $this->connection->createQueryBuilder();
$qb->select('DISTINCT c.id_customer', 'c.email', 'c.firstname', 'c.lastname')
    ->from(_DB_PREFIX_ . 'orders', 'o')
    ->innerJoin('o', _DB_PREFIX_ . 'customer', 'c', 'o.id_customer = c.id_customer')
    ->innerJoin('o', _DB_PREFIX_ . 'order_state', 'os', 'o.current_state = os.id_order_state')
    ->where('os.logable = 1')  // ← CRITICAL: only count logable orders
    ->andWhere('o.total_paid_real >= :minAmount')
    ->andWhere('c.deleted = 0')
    ->setParameter('minAmount', $minAmount);
```

### Raw SQL pattern (legacy)

```php
// ✅ CORRECT
$sql = '
SELECT COUNT(*) AS orders
FROM `' . _DB_PREFIX_ . 'orders` o
LEFT JOIN `' . _DB_PREFIX_ . 'order_state` os ON o.current_state = os.id_order_state
WHERE `invoice_date` BETWEEN "' . pSQL($date_from) . ' 00:00:00" 
  AND "' . pSQL($date_to) . ' 23:59:59" 
  AND os.logable = 1
';
```

### ❌ WRONG patterns to avoid

```php
// ❌ WRONG — hardcoded state IDs, breaks when states are customized
->where('o.current_state IN (:validStates)')
->setParameter('validStates', [2, 3, 4, 5], Connection::PARAM_INT_ARRAY)

// ❌ WRONG — no state filtering at all, includes cancelled/pending orders
$qb->select('COUNT(*)')
    ->from(_DB_PREFIX_ . 'orders', 'o')
    ->where('o.total_paid_real > 0');

// ❌ WRONG — using Configuration::get('PS_OS_PAYMENT') etc.
// This only gives you ONE state, not all logable states
->where('o.current_state = :state')
->setParameter('state', Configuration::get('PS_OS_PAYMENT'))
```

### Why not hardcode state IDs?

1. **Customizable**: Shop owners can modify order states or add custom ones
2. **Multi-state support**: Multiple states can be logable (payment, shipped, delivered)
3. **PrestaShop updates**: State IDs may change between versions or installations
4. **Consistency**: Your module statistics will match PrestaShop's dashboard

### Reference implementation

See `/controllers/admin/AdminStatsController.php` for PrestaShop's official implementation:
- `AdminStatsController::getOrders()` (line ~267)
- `AdminStatsController::getTotalSales()` (line ~214)
- All methods use `os.logable = 1`

### When to use this pattern

Use the logable pattern whenever you:
- Generate statistics or reports based on orders
- Calculate customer eligibility based on past orders
- Count "valid" or "completed" orders
- Match PrestaShop's dashboard/statistics behavior
- Query orders for analytics or KPIs

**Do NOT use** the logable pattern when:
- You need ALL orders regardless of state (admin order list)
- You specifically want to query cancelled/pending orders
- You're working with order management (not statistics)

## Resources

- [Doctrine ORM in PrestaShop](https://devdocs.prestashop-project.org/9/development/architecture/domain/data-layer/)
- [ObjectModel reference](https://devdocs.prestashop-project.org/9/development/components/database/objectmodel/)
- [AdminStatsController reference](https://github.com/PrestaShop/PrestaShop/blob/develop/controllers/admin/AdminStatsController.php)
