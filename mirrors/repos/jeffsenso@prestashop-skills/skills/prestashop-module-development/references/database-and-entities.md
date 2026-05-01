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

## Resources

- [Doctrine ORM in PrestaShop](https://devdocs.prestashop-project.org/9/development/architecture/domain/data-layer/)
- [ObjectModel reference](https://devdocs.prestashop-project.org/9/development/components/database/objectmodel/)
