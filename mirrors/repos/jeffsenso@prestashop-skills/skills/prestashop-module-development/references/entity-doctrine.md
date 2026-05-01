# Doctrine Entity pattern (translatable entities)

## ObjectModel vs Doctrine ORM — differences and when to use each

| | **ObjectModel** (legacy) | **Doctrine ORM** (modern) |
|---|---|---|
| Definition | PHP class with a static `$definition` array | PHP class with `@ORM\` annotations |
| Multilang | `'multilang' => true` + `_lang` table via PS convention | Separate `*Lang` entity with `@ORM\ManyToOne` |
| Repository | Static methods or raw `Db::getInstance()` | Typed `EntityRepository`, injectable via DI |
| DI / testability | Not injectable — `new Entity($id)` | Repository + Manager injected via services.yml |
| Lifecycle hooks | `add()`, `update()`, `delete()` overrideable | `@ORM\PrePersist`, `@ORM\PreUpdate` |
| Shop association | Manual raw SQL | Manual via Manager (same approach, cleaner) |
| PS upgrade safety | Tightly coupled to PS ObjectModel internals | Decoupled — survives PS major version changes |

**Use Doctrine ORM when:**
- The entity is managed via the Grid system (CRUD list page)
- You want proper DI (repository + manager injected into services)
- The entity has translatable fields (`*Lang` table)
- You want lifecycle hooks (`dateAdd`, `dateUpd` auto-managed)

---

## Table naming convention — MANDATORY

Every module table name MUST start with `ws_`. This groups all Websenso tables together in the database and avoids conflicts with PS core tables.

- `ws_mymodule_items` ✅
- `ws_mymodule_items_lang` ✅
- `ws_mymodule_items_shop` ✅
- `mymodule_items` ❌ (missing ws_ prefix)

---

## How the entity class name maps to the table name

**Do NOT use `MetadataListener` or Doctrine Event Listeners to set table names.**

PrestaShop's Doctrine integration automatically adds `_DB_PREFIX_` to all entity table names globally. The entity class name (lowercased by Doctrine) becomes the table name:

```
PHP class: Ws_mymodule_items
  → Doctrine lowercases → ws_mymodule_items
  → PS adds _DB_PREFIX_ → ps_ws_mymodule_items  (full DB table name)
```

So the naming convention is: **PHP class name = table name without `_DB_PREFIX_`**.

Use `@ORM\Table()` with **no `name=` parameter** — Doctrine derives it automatically.

The SQL in `SqlQueries.php` uses `_DB_PREFIX_ . 'ws_mymodule_items'` which produces the exact same table.

---

## Full Doctrine entity structure

```
src/
 Entity/
   ├── Ws_mymodule_items.php           # class name = table name
   └── Ws_mymodule_items_lang.php      # class name = lang table name
 Repository/
   └── MymoduleItemsRepository.php     # extends EntityRepository
 Manager/
    └── MymoduleItemsManager.php        # upsert logic, injects langRepository
config/
 common.yml                          # repository factory
 services.yml                        # manager + form chain
```

---

## `src/Entity/Ws_mymodule_items.php`

```php
namespace Ws\Mymodule\Entity;

use DateTime;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\ORM\Mapping as ORM;

/**
 * @ORM\Entity(repositoryClass="Ws\Mymodule\Repository\MymoduleItemsRepository")
 * @ORM\HasLifecycleCallbacks
 * @ORM\Table()
 */
class Ws_mymodule_items
{
    /**
     * @ORM\Id
     * @ORM\Column(name="id_mymodule_items", type="integer")
     * @ORM\GeneratedValue(strategy="AUTO")
     */
    private int $id;

    /**
     * @ORM\OneToMany(
     *     targetEntity="Ws\Mymodule\Entity\Ws_mymodule_items_lang",
     *     cascade={"persist","remove"},
     *     mappedBy="ws_mymodule_items"
     * )
     */
    private $langs;

    /**
     * @ORM\Column(name="active", type="boolean", options={"default": false})
     */
    private bool $active = false;

    /**
     * @ORM\Column(name="position", type="integer")
     */
    private int $position = 0;

    /**
     * @ORM\Column(name="date_add", type="datetime")
     */
    private DateTime $dateAdd;

    /**
     * @ORM\Column(name="date_upd", type="datetime")
     */
    private DateTime $dateUpd;

    public function __construct()
    {
        $this->langs = new ArrayCollection();
    }

    public function getId(): int { return $this->id; }
    public function isActive(): bool { return $this->active; }
    public function setActive(bool $active): void { $this->active = $active; }
    public function getPosition(): int { return $this->position; }
    public function setPosition(int $position): self { $this->position = $position; return $this; }
    public function getLangs() { return $this->langs; }

    public function getLangByLangId(int $langId): ?Ws_mymodule_items_lang
    {
        foreach ($this->langs as $lang) {
            if ($langId === $lang->getLang()->getId()) {
                return $lang;
            }
        }
        return null;
    }

    public function addLang(Ws_mymodule_items_lang $lang): self
    {
        $lang->setWs_mymodule_items($this);
        $this->langs->add($lang);
        return $this;
    }

    public function getAllFields(): array
    {
        $names = [];
        foreach ($this->langs as $l) {
            $names[$l->getLang()->getId()] = $l->getName();
        }
        return [
            'name'   => $names,
            'active' => $this->active,
        ];
    }

    public function setFields(array $params): void
    {
        if (isset($params['active'])) {
            $this->active = (bool) $params['active'];
        }
        if (isset($params['position'])) {
            $this->position = (int) $params['position'];
        }
    }

    /** @ORM\PrePersist */
    public function setCreatedAt(): void
    {
        $this->dateAdd = new DateTime();
        $this->dateUpd = new DateTime();
    }

    /** @ORM\PreUpdate */
    public function setUpdatedAt(): void
    {
        $this->dateUpd = new DateTime();
    }
}
```

---

## `src/Entity/Ws_mymodule_items_lang.php`

```php
namespace Ws\Mymodule\Entity;

use Doctrine\ORM\Mapping as ORM;
use PrestaShopBundle\Entity\Lang;

/**
 * @ORM\Entity()
 * @ORM\Table()
 */
class Ws_mymodule_items_lang
{
    /**
     * @ORM\Id
     * @ORM\ManyToOne(targetEntity="Ws\Mymodule\Entity\Ws_mymodule_items", inversedBy="langs")
     * @ORM\JoinColumn(name="id_mymodule_items", referencedColumnName="id_mymodule_items", nullable=false)
     */
    private Ws_mymodule_items $ws_mymodule_items;

    /**
     * @ORM\Id
     * @ORM\ManyToOne(targetEntity="PrestaShopBundle\Entity\Lang")
     * @ORM\JoinColumn(name="id_lang", referencedColumnName="id_lang", nullable=false, onDelete="CASCADE")
     */
    private Lang $lang;

    /**
     * @ORM\Column(type="string", length=255, nullable=true)
     */
    private ?string $name = null;

    public function getWs_mymodule_items(): Ws_mymodule_items { return $this->ws_mymodule_items; }
    public function setWs_mymodule_items(Ws_mymodule_items $e): self { $this->ws_mymodule_items = $e; return $this; }
    public function getLang(): Lang { return $this->lang; }
    public function setLang(Lang $l): self { $this->lang = $l; return $this; }
    public function getName(): ?string { return $this->name; }
    public function setName(?string $name): self { $this->name = $name; return $this; }
}
```

---

## `src/Repository/MymoduleItemsRepository.php`

```php
namespace Ws\Mymodule\Repository;

use Doctrine\ORM\EntityRepository;
use Ws\Mymodule\Entity\Ws_mymodule_items;

class MymoduleItemsRepository extends EntityRepository
{
    public function upsertEntity(Ws_mymodule_items $entity): void
    {
        $em = $this->getEntityManager();
        $em->persist($entity);
        $em->flush();
    }

    public function deleteEntity(Ws_mymodule_items $entity): void
    {
        $em = $this->getEntityManager();
        $em->remove($entity);
        $em->flush();
    }

    public function getNextPosition(): int
    {
        $max = $this->createQueryBuilder('e')
            ->select('MAX(e.position)')
            ->getQuery()
            ->getSingleScalarResult();

        // IMPORTANT: PrestaShop positions are 0-based
        // First item = position 0, second = 1, third = 2, etc.
        // Grid displays them as 1, 2, 3... but DB stores 0, 1, 2...
        return ($max !== null) ? ((int) $max + 1) : 0;
    }

    /** Used by Grid QueryBuilder — raw DBAL */
    public function getByIdAndLang(?int $id, int $langId): array
    {
        $conn   = $this->getEntityManager()->getConnection();
        $prefix = _DB_PREFIX_;
        $params = ['id_lang' => $langId];
        $filter = '';
        if ($id && $id > 0) {
            $filter = ' AND e.id_mymodule_items = :id';
            $params['id'] = $id;
        }
        $sql = "SELECT e.*, el.*
                FROM {$prefix}ws_mymodule_items e
                LEFT JOIN {$prefix}ws_mymodule_items_lang el
                    ON e.id_mymodule_items = el.id_mymodule_items AND el.id_lang = :id_lang
                WHERE e.active = 1{$filter}
                ORDER BY e.position ASC";

        return $conn->prepare($sql)->executeQuery($params)->fetchAllAssociative();
    }
}
```

---

## `src/Manager/MymoduleItemsManager.php`

```php
namespace Ws\Mymodule\Manager;

use PrestaShopBundle\Entity\Repository\LangRepository;
use Ws\Mymodule\Entity\Ws_mymodule_items;
use Ws\Mymodule\Entity\Ws_mymodule_items_lang;
use Ws\Mymodule\Repository\MymoduleItemsRepository;

class MymoduleItemsManager
{
    public function __construct(
        private readonly MymoduleItemsRepository $repository,
        private readonly LangRepository $langRepository,
    ) {}

    public function upsert(int $id, array $params): void
    {
        $entity = $this->repository->findOneBy(['id' => $id]);

        if (!$entity) {
            $entity = new Ws_mymodule_items();
            foreach ($params['name'] as $langId => $name) {
                $lang    = $this->langRepository->findOneBy(['id' => $langId]);
                $langRow = new Ws_mymodule_items_lang();
                $langRow->setLang($lang);
                $entity->addLang($langRow);
            }
            if (!isset($params['position'])) {
                $params['position'] = $this->repository->getNextPosition();
            }
        }

        foreach ($params['name'] as $langId => $value) {
            $row = $entity->getLangByLangId((int) $langId);
            if ($row !== null) {
                $row->setName($value);
            }
        }
        unset($params['name']);
        $entity->setFields($params);
        $this->repository->upsertEntity($entity);
    }

    public function delete(int $id): void
    {
        $entity = $this->repository->findOneBy(['id' => $id]);
        if ($entity) {
            $this->repository->deleteEntity($entity);
        }
    }

    public function getActiveLanguages(): array
    {
        return $this->langRepository->findBy(['active' => true]);
    }
}
```

---

## `config/common.yml` — repository factory

No MetadataListener. No special Doctrine event listener. Just the factory:

```yaml
services:
  mymodule.repository.items_repository:
    class: Ws\Mymodule\Repository\MymoduleItemsRepository
    public: true
    factory: ["@doctrine.orm.default_entity_manager", getRepository]
    arguments:
      - Ws\Mymodule\Entity\Ws_mymodule_items
```

---

## `config/services.yml` additions — manager

```yaml
imports:
  - { resource: common.yml }

services:
  mymodule.manager.items_manager:
    class: Ws\Mymodule\Manager\MymoduleItemsManager
    public: true
    arguments:
      - "@mymodule.repository.items_repository"
      - "@prestashop.core.admin.lang.repository"
```

---

## Key rules summary

- Entity class name = table name without `_DB_PREFIX_` (PS handles the prefix globally)
- Always prefix tables with `ws_`: `ws_mymodule_*`
- `@ORM\Table()` — empty annotation, NO `name=` parameter
- Do NOT create `MetadataListener` or Doctrine event listeners for table naming
- Repository registered via factory: `["@doctrine.orm.default_entity_manager", getRepository]`
- Manager injects `@prestashop.core.admin.lang.repository` for translatable entities
- Both entity files (main + lang) have the `if (!defined('_PS_VERSION_')) { exit; }` guard
- **Position field MUST start at 0** (not 1) — Grid displays as 1, 2, 3... but DB stores 0, 1, 2...
  - `getNextPosition()` should return `0` when no records exist (not `1`)
  - FixturesInstaller should set first item position to `0` (not `1`)
  - SQL `DEFAULT 0` is correct for position column
