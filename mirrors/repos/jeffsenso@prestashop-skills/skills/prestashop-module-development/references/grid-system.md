# PrestaShop Grid system

The PS Grid system renders CRUD list pages using `@PrestaShop/Admin/Common/Grid/grid_panel.html.twig`. It handles columns, filters, bulk actions, pagination, toggling, and drag-and-drop position — all with zero custom JS when paired with the pre-built bundle.

## File structure

```
src/Grid/
├── Definition/Factory/
│   └── MyEntityGridDefinitionFactory.php   # columns, filters, row actions
├── Filters/
│   └── MyEntityFilters.php                 # default sort/pagination
└── Query/
    └── MyEntityQueryBuilder.php            # Doctrine DBAL query
views/js/
└── mymodule.bundle.js                      # pre-built Grid JS bundle
```

All `src/Grid/` subdirectories must have an `index.php` guard (lotr adds them automatically).

---

## GridDefinitionFactory

```php
namespace Vs\MyModule\Grid\Definition\Factory;

use PrestaShop\PrestaShop\Core\Grid\Action\GridActionCollection;
use PrestaShop\PrestaShop\Core\Grid\Action\GridActionCollectionInterface;
use PrestaShop\PrestaShop\Core\Grid\Action\Row\RowActionCollection;
use PrestaShop\PrestaShop\Core\Grid\Action\Row\Type\LinkRowAction;
use PrestaShop\PrestaShop\Core\Grid\Action\Row\Type\SubmitRowAction;
use PrestaShop\PrestaShop\Core\Grid\Action\Type\SimpleGridAction;
use PrestaShop\PrestaShop\Core\Grid\Column\ColumnCollection;
use PrestaShop\PrestaShop\Core\Grid\Column\ColumnCollectionInterface;
use PrestaShop\PrestaShop\Core\Grid\Column\Type\Common\ActionColumn;
use PrestaShop\PrestaShop\Core\Grid\Column\Type\Common\DataColumn;
use PrestaShop\PrestaShop\Core\Grid\Column\Type\Common\PositionColumn;
use PrestaShop\PrestaShop\Core\Grid\Column\Type\Common\ToggleColumn;
use PrestaShop\PrestaShop\Core\Grid\Definition\Factory\AbstractGridDefinitionFactory;
use PrestaShop\PrestaShop\Core\Grid\Filter\Filter;
use PrestaShop\PrestaShop\Core\Grid\Filter\FilterCollection;
use PrestaShop\PrestaShop\Core\Grid\Filter\FilterCollectionInterface;
use PrestaShopBundle\Form\Admin\Type\SearchAndResetType;
use Symfony\Component\Form\Extension\Core\Type\TextType;

class MyEntityGridDefinitionFactory extends AbstractGridDefinitionFactory
{
    public const GRID_ID = 'mymodule_myentity';

    protected function getId(): string { return self::GRID_ID; }
    protected function getName(): string { return $this->trans('My Entities', [], 'Modules.Mymodule.Admin'); }

    protected function getColumns(): ColumnCollectionInterface
    {
        return (new ColumnCollection())
            ->add((new DataColumn('id_myentity'))
                ->setName($this->trans('ID', [], 'Admin.Global'))
                ->setOptions(['field' => 'id_myentity'])
            )
            ->add((new DataColumn('name'))
                ->setName($this->trans('Name', [], 'Admin.Global'))
                ->setOptions(['field' => 'name'])
            )
            // Drag-and-drop position column
            ->add((new PositionColumn('position'))
                ->setName($this->trans('Position', [], 'Admin.Global'))
                ->setOptions([
                    'id_field' => 'id_myentity',
                    'position_field' => 'position',
                    'update_method' => 'POST',
                    'update_route' => 'mymodule_myentity_update_position',
                    'record_route_params' => ['id_myentity' => 'entityId'],
                ])
            )
            // Toggle active/inactive column
            ->add((new ToggleColumn('active'))
                ->setName($this->trans('Active', [], 'Admin.Global'))
                ->setOptions([
                    'field' => 'active',
                    'primary_field' => 'id_myentity',
                    'route' => 'mymodule_myentity_toggle_status',
                    'route_param_name' => 'entityId',  // controller must declare: int $entityId
                ])
            )
            ->add((new ActionColumn('actions'))
                ->setName($this->trans('Actions', [], 'Admin.Global'))
                ->setOptions(['actions' => (new RowActionCollection())
                    ->add((new LinkRowAction('edit'))
                        ->setName($this->trans('Edit', [], 'Admin.Actions'))
                        ->setIcon('edit')
                        ->setOptions([
                            'route' => 'mymodule_myentity_edit',
                            'route_param_name' => 'entityId',
                            'route_param_field' => 'id_myentity',
                            'clickable_row' => true,
                        ])
                    )
                    ->add((new SubmitRowAction('delete'))
                        ->setName($this->trans('Delete', [], 'Admin.Actions'))
                        ->setIcon('delete')
                        ->setOptions([
                            'method' => 'POST',
                            'route' => 'mymodule_myentity_delete',
                            'route_param_name' => 'entityId',
                            'route_param_field' => 'id_myentity',
                            'confirm_message' => $this->trans('Delete selected item?', [], 'Admin.Notifications.Warning'),
                        ])
                    ),
                ])
            );
    }

    // IMPORTANT: return FilterCollectionInterface (not FilterCollection) — PHPStan requirement
    protected function getFilters(): FilterCollectionInterface
    {
        return (new FilterCollection())
            ->add((new Filter('id_myentity', TextType::class))
                ->setTypeOptions(['required' => false])
                ->setAssociatedColumn('id_myentity')
            )
            ->add((new Filter('name', TextType::class))
                ->setTypeOptions(['required' => false])
                ->setAssociatedColumn('name')
            )
            // YesAndNoChoiceType — for ToggleColumn (active, showOnHp, etc.)
            // Renders a Yes/No dropdown filter. Use for any boolean/toggle column.
            ->add((new Filter('active', YesAndNoChoiceType::class))
                ->setTypeOptions(['required' => false])
                ->setAssociatedColumn('active')
            )
            // ReorderPositionsButtonType — for PositionColumn
            // Renders a "Rearrange" button in the filter row. Clicking it resets the grid
            // sort to 'position' ASC, which re-enables drag-and-drop (position_handle column
            // is only injected by GridPresenter when orderBy === 'position').
            // This is the proper UX fix for "drag disabled after sorting by another column".
            ->add((new Filter('position', ReorderPositionsButtonType::class))
                ->setAssociatedColumn('position')
            )
            ->add((new Filter('actions', SearchAndResetType::class))
                ->setTypeOptions([
                    'reset_route' => 'admin_common_reset_search_by_filter_id',
                    'reset_route_params' => ['filterId' => self::GRID_ID],
                    'redirect_route' => 'mymodule_myentity_index',
                ])
                ->setAssociatedColumn('actions')
            );
    }

    // IMPORTANT: return GridActionCollectionInterface (not GridActionCollection) — PHPStan requirement
    protected function getGridActions(): GridActionCollectionInterface
    {
        return (new GridActionCollection())
            ->add((new SimpleGridAction('common_refresh_list'))
                ->setName($this->trans('Refresh list', [], 'Admin.Advparameters.Feature'))
                ->setIcon('refresh')
            );
    }
}
```

---

## QueryBuilder (Doctrine DBAL)

```php
namespace Vs\MyModule\Grid\Query;

use Doctrine\DBAL\Connection;
use Doctrine\DBAL\Query\QueryBuilder;
use PrestaShop\PrestaShop\Core\Grid\Query\AbstractDoctrineQueryBuilder;
use PrestaShop\PrestaShop\Core\Grid\Query\DoctrineSearchCriteriaApplicatorInterface;
use PrestaShop\PrestaShop\Core\Grid\Search\SearchCriteriaInterface;

class MyEntityQueryBuilder extends AbstractDoctrineQueryBuilder
{
    public function __construct(
        Connection $connection,
        string $dbPrefix,
        private DoctrineSearchCriteriaApplicatorInterface $searchCriteriaApplicator,
        private int $contextShopId,
        private int $contextIdLang
    ) {
        parent::__construct($connection, $dbPrefix);
    }

    public function getSearchQueryBuilder(SearchCriteriaInterface $searchCriteria): QueryBuilder
    {
        $qb = $this->getBaseQueryBuilder($searchCriteria->getFilters());
        $qb->select('e.id_myentity, e.position, e.active, el.name')
           ->groupBy('e.id_myentity');
        $this->searchCriteriaApplicator
            ->applySorting($searchCriteria, $qb)
            ->applyPagination($searchCriteria, $qb);
        return $qb;
    }

    public function getCountQueryBuilder(SearchCriteriaInterface $searchCriteria): QueryBuilder
    {
        return $this->getBaseQueryBuilder($searchCriteria->getFilters())
            ->select('COUNT(DISTINCT e.id_myentity)');
    }

    private function getBaseQueryBuilder(array $filters): QueryBuilder
    {
        // Use leftJoin (not innerJoin) so rows without lang/shop entries still appear.
        $qb = $this->connection->createQueryBuilder()
            ->from($this->dbPrefix . 'mymodule_myentity', 'e')
            ->leftJoin('e', $this->dbPrefix . 'mymodule_myentity_lang', 'el',
                'e.id_myentity = el.id_myentity AND el.id_lang = :id_lang')
            ->leftJoin('e', $this->dbPrefix . 'mymodule_myentity_shop', 'es',
                'e.id_myentity = es.id_myentity AND es.id_shop = :id_shop')
            ->setParameter('id_lang', $this->contextIdLang)
            ->setParameter('id_shop', $this->contextShopId);

        if (isset($filters['id_myentity'])) {
            $qb->andWhere('e.id_myentity = :id_myentity')
               ->setParameter('id_myentity', $filters['id_myentity']);
        }
        if (isset($filters['name'])) {
            $qb->andWhere('el.name LIKE :name')
               ->setParameter('name', '%' . $filters['name'] . '%');
        }

        return $qb;
    }
}
```

---

## Filters class

```php
namespace Vs\MyModule\Grid\Filters;

use PrestaShop\PrestaShop\Core\Search\Filters;
use Vs\MyModule\Grid\Definition\Factory\MyEntityGridDefinitionFactory;

class MyEntityFilters extends Filters
{
    protected $filterId = MyEntityGridDefinitionFactory::GRID_ID;

    public static function getDefaults(): array
    {
        return [
            'limit'     => 20,
            'offset'    => 0,
            'orderBy'   => 'position',
            'sortOrder' => 'asc',
            'filters'   => [],
        ];
    }
}
```

---

## `config/services.yml` registration

```yaml
  # Grid definition factory
  mymodule.grid.definition.factory.myentity:
    class: 'Vs\MyModule\Grid\Definition\Factory\MyEntityGridDefinitionFactory'
    parent: 'prestashop.core.grid.definition.factory.abstract_grid_definition'

  # Query builder
  mymodule.grid.query.myentity:
    class: 'Vs\MyModule\Grid\Query\MyEntityQueryBuilder'
    parent: 'prestashop.core.grid.abstract_query_builder'
    arguments:
      - '@prestashop.core.query.doctrine_search_criteria_applicator'
      - "@=service('prestashop.adapter.shop.context').getContextListShopID()[0]"
      - "@=service('prestashop.adapter.legacy.context').getContext().language.id"

  # DoctrineGridDataFactory — 4th arg must match GRID_ID
  mymodule.grid.data.factory.myentity:
    class: 'PrestaShop\PrestaShop\Core\Grid\Data\Factory\DoctrineGridDataFactory'
    arguments:
      - '@mymodule.grid.query.myentity'
      - '@prestashop.core.hook.dispatcher'
      - '@prestashop.core.grid.query.doctrine_query_parser'
      - 'mymodule_myentity'

  # GridFactory — injected into the controller
  mymodule.grid.factory.myentity:
    class: 'PrestaShop\PrestaShop\Core\Grid\GridFactory'
    arguments:
      - '@mymodule.grid.definition.factory.myentity'
      - '@mymodule.grid.data.factory.myentity'
      - '@prestashop.core.grid.filter.form_factory'
      - '@prestashop.core.hook.dispatcher'

  # PositionDefinition — used by updatePositionAction
  # IMPORTANT: $table must be the table name WITHOUT the DB prefix.
  # DoctrinePositionUpdateHandler prepends $dbPrefix automatically at runtime.
  # e.g. for table `9sxtm_prefix_mymodule_items`, use $table: 'prefix_mymodule_items'
  mymodule.grid.position_definition:
    class: 'PrestaShop\PrestaShop\Core\Grid\Position\PositionDefinition'
    arguments:
      $table: 'mymodule_myentity'   # WITHOUT _DB_PREFIX_ — handler adds it
      $idField: 'id_myentity'       # actual DB column name of the PK
      $positionField: 'position'
```

---

## `config/routes.yml` — required routes

```yaml
# CRITICAL: Do NOT start paths with /modules/
# PS's YamlModuleLoader (src/PrestaShopBundle/Routing/YamlModuleLoader.php) automatically
# prepends /modules to every route path. Starting your path with /modules/ results in
# /modules/modules/mymodule/... which causes 405 Method Not Allowed on all actions.

mymodule_myentity_index:
  path: /mymodule/entities          # becomes /modules/mymodule/entities after PS prefix
  methods: [GET]
  defaults:
    _controller: 'Vs\MyModule\Controller\Admin\MyEntityController::indexAction'
    _legacy_controller: AdminMymoduleMyentity
    _legacy_link: AdminMymoduleMyentity

# Search uses SAME path as index, just POST method.
# The Grid search form POSTs to the current URL (index URL) — it MUST match here.
mymodule_myentity_search:
  path: /mymodule/entities          # same as index — PS Grid POSTs to the same URL
  methods: [POST]
  defaults:
    _controller: 'Vs\MyModule\Controller\Admin\MyEntityController::searchAction'
    _legacy_controller: AdminMymoduleMyentity
    _legacy_link: AdminMymoduleMyentity:search

# Toggle route — entityId comes from ToggleColumn's route_param_name
mymodule_myentity_toggle_status:
  path: /mymodule/entities/{entityId}/toggle-status
  methods: [POST]
  defaults:
    _controller: 'Vs\MyModule\Controller\Admin\MyEntityController::toggleStatus'
    _legacy_controller: AdminMymoduleMyentity
    _legacy_link: AdminMymoduleMyentity:togglestatus
  requirements:
    entityId: '\d+'

# Position update POSTed by the PS drag-and-drop bundle
mymodule_myentity_update_position:
  path: /mymodule/entities/update-position
  methods: [POST]
  defaults:
    _controller: 'Vs\MyModule\Controller\Admin\MyEntityController::updatePositionAction'
    _legacy_controller: AdminMymoduleMyentity
    _legacy_link: AdminMymoduleMyentity:updateposition
```

---

## Controller actions

```php
use PrestaShop\PrestaShop\Core\Exception\TranslatableCoreException;
use PrestaShop\PrestaShop\Core\Grid\Position\GridPositionUpdaterInterface;
use PrestaShop\PrestaShop\Core\Grid\Position\PositionUpdateFactoryInterface;
use Symfony\Component\HttpFoundation\RedirectResponse;

// PS resolves MyEntityFilters via its Filters resolver (injected automatically)
public function indexAction(MyEntityFilters $filters): Response
{
    $gridFactory = $this->get('mymodule.grid.factory.myentity');
    return $this->render('@Modules/mymodule/views/templates/admin/myentity/index.html.twig', [
        'enableSidebar' => true,
        'layoutTitle' => $this->trans('My Entities', [], 'Modules.Mymodule.Admin'),
        'layoutHeaderToolbarBtn' => [
            'add' => [
                'desc' => $this->trans('Add new entity', [], 'Modules.Mymodule.Admin'),
                'icon' => 'add_circle_outline',
                'href' => $this->generateUrl('mymodule_myentity_create'),
            ],
        ],
        'grid' => $this->presentGrid($gridFactory->getGrid($filters)),
    ]);
}

public function searchAction(Request $request): RedirectResponse
{
    $definitionFactory = $this->get('mymodule.grid.definition.factory.myentity');
    $responseBuilder   = $this->get('prestashop.bundle.grid.response_builder');
    return $responseBuilder->buildSearchResponse(
        $definitionFactory,
        $request,
        MyEntityGridDefinitionFactory::GRID_ID,
        'mymodule_myentity_index'
    );
}

// entityId comes from route parameter (ToggleColumn sets route_param_name)
public function toggleStatus(Request $request, int $entityId): Response
{
    // load entity, toggle ->active, save, return JSON
    return $this->json(['status' => true, 'message' => $this->trans('Status updated.', [], 'Admin.Notifications.Success')]);
}

public function updatePositionAction(Request $request): RedirectResponse
{
    // IMPORTANT: use request->all()['positions'] NOT request->get('positions')
    // Symfony InputBag::get() throws BadRequestException on array values.
    $positionsData      = ['positions' => $request->request->all()['positions'] ?? []];
    $positionDefinition = $this->get('mymodule.grid.position_definition');
    $positionUpdateFactory = $this->get(PositionUpdateFactoryInterface::class);

    try {
        $positionUpdate = $positionUpdateFactory->buildPositionUpdate($positionsData, $positionDefinition);
        $this->get(GridPositionUpdaterInterface::class)->update($positionUpdate);
        $this->addFlash('success', $this->trans('Successful update.', [], 'Admin.Notifications.Success'));
    } catch (TranslatableCoreException $e) {
        $this->flashErrors([$e->toArray()]);
    } catch (\Exception $e) {
        $this->flashErrors([$e->getMessage()]);
    }

    return $this->redirectToRoute('mymodule_myentity_index');
}
```

---

## Twig template (`index.html.twig`)

```twig
{% extends '@PrestaShop/Admin/layout.html.twig' %}

{% block content %}
    <div class="row">
        <div class="col">
            {% include '@PrestaShop/Admin/Common/Grid/grid_panel.html.twig' with {'grid': grid} %}
        </div>
    </div>
{% endblock %}

{% block javascripts %}
    {{ parent() }}
    {# Load the Grid bundle ONLY here — never also in hookDisplayBackOfficeHeader #}
    <script src="{{ asset('../modules/mymodule/views/js/mymodule.bundle.js') }}"></script>
    <script src="{{ asset('themes/default/js/bundle/pagination.js') }}"></script>
{% endblock %}
```

> **CRITICAL — load the bundle ONLY in the Twig `{% block javascripts %}`, NEVER also in `hookDisplayBackOfficeHeader`.**
> Loading it in both places registers `AsyncToggleColumnExtension` twice. Each toggle click fires two AJAX calls that cancel each other out — the DB ends up unchanged while the UI shows success. This is silent and hard to debug.

> ⚠️ **Asset path pitfall**: the path `../modules/mymodule/views/js/mymodule.bundle.js` must use the **exact module folder name** (i.e. `$this->name`). A typo here (e.g. `ws_mymodule` instead of `wsmymodule`) causes a silent 404 — the bundle is not loaded, toggle and drag-and-drop silently stop working.

---

## JS bundle setup

The pre-built bundle template is in `skills/.agents/skills/prestashop-module-development/scripts/grid.bundle.js`. Copy it and replace the two `GRID_ID_PLACEHOLDER` occurrences with your `GRID_ID`:

```bash
cp vendor/websenso/prestashop-module-devtools/skills/.agents/skills/prestashop-module-development/scripts/grid.bundle.js \
   views/js/{modulename}.bundle.js

# Replace the internal webpack grid ID (inside the minified section)
sed -i 's/new o\.a("GRID_ID_PLACEHOLDER")/new o.a("{mymodule_myentity}")/g' views/js/{modulename}.bundle.js
# Replace the $(document).ready grid ID (bottom of file)
sed -i "s/prestashop\.component\.Grid('GRID_ID_PLACEHOLDER')/prestashop.component.Grid('{mymodule_myentity}')/g" views/js/{modulename}.bundle.js

# VERIFY — grep must show 0 for GRID_ID_PLACEHOLDER and 2+ for your real GRID_ID.
# If sed matched nothing (0 replacements) the ID inside the minified section is
# NOT the literal string "GRID_ID_PLACEHOLDER" — it's a leftover real ID from
# whatever module the template/bundle was last copied from (e.g. "wsblocksinhooks_block").
# In that case sed silently does nothing and the bug below happens.
grep -c 'GRID_ID_PLACEHOLDER' views/js/{modulename}.bundle.js   # expect: 0
grep -c '"{mymodule_myentity}"' views/js/{modulename}.bundle.js  # expect: >=1 (inside minified bootstrap)
```

**CRITICAL — Grid ID must match `GRID_ID` constant exactly:**
- Replace both `GRID_ID_PLACEHOLDER` occurrences with the exact value of `YourGridDefinitionFactory::GRID_ID` (e.g. `'wsfaq_question'`).
- Mismatch causes all extensions (toggles, position drag-and-drop, bulk actions, **column sort, search reset**) to silently fail — no JS error is thrown, clicks just do nothing.

> **The #1 real-world cause of "sort doesn't work" / "reset doesn't work": a bundle copied from another module still has that OTHER module's ID hardcoded inside the minified webpack bootstrap** (the `new o.a("...")` call), and it is NOT the literal text `GRID_ID_PLACEHOLDER` — it's a real ID like `"wsblocksinhooks_block"` or `"wsimageslider"`. Because it doesn't match the `GRID_ID_PLACEHOLDER` pattern, the `sed` replacement above finds nothing and silently changes 0 occurrences. Always run the verification `grep -c` commands above, and if `GRID_ID_PLACEHOLDER` count isn't 0, manually find and fix the literal ID:
> ```bash
> # Find the literal ID actually baked into the minified bootstrap
> grep -o '(0, window\.\$)([^;]*;' views/js/{modulename}.bundle.js
> # Fix it directly once you spot it (replace the wrong-but-real old ID)
> sed -i 's/new o\.a("OLD_WRONG_ID")/new o.a("{mymodule_myentity}")/' views/js/{modulename}.bundle.js
> ```

> **Do NOT** use `addJqueryUI('ui.sortable')` + custom admin.js for position management. Use the PS Grid PositionColumn + the bundle — it is fully handled by the framework.

---

## How sort, search and reset actually work (and how they silently break)

Every compiled `{modulename}.bundle.js` contains **two independent init blocks** that both need the correct Grid ID:

1. **The minified webpack bootstrap** (the huge single-line section near the top, ending in `e(e.s = 13)` and a giant module array). Buried inside it is a line like:
   ```js
   (0, window.$)(function () { var n = new o.a("GRID_ID"); n.addExtension(new a.a), n.addExtension(new c.a), /* ...9 total */ })
   ```
   This runs **immediately when the script loads** (it does not wait for `window.prestashop.component` to exist — it uses the bundle's own private, bundled copies of the `Grid` class and all 9 standard extension classes). These 9 extensions cover:
   - `SubmitRowActionExtension` — row delete/submit buttons (`.js-submit-row-action`)
   - `BulkActionExtension` — enable/disable the bulk action button based on checkbox state
   - `CommonGridActionExtension` — "show SQL query" modal
   - `ResetSearchExtension` — **the reset button** (`.js-reset-search`): POSTs to `data-url`, then `window.location.assign(data-redirect)` on success
   - `LinkRowActionExtension` — clickable rows + confirm dialogs
   - `CommonRefreshListExtension` — "Refresh list" grid action button
   - `SortableColumnExtension` — **column header click-to-sort** (`.ps-sortable-column`): reads `data-sort-col-name` / `data-sort-prefix` / current `data-sort-direction`, builds a new URL with `{prefix}[orderBy]` and `{prefix}[sortOrder]` query params, and does a full `window.location =` navigation (sort is a page reload, not AJAX)
   - `GridActionExtension` — grid-level action submit buttons
   - `BulkActionSubmitButtonExtension` — bulk action form submit

   **This single hardcoded ID is what makes sort and reset work.** `Grid.getContainer()` resolves to `$("#" + id + "_grid")`; if this ID doesn't match the real DOM container (`{GRID_ID}_grid`, rendered by `grid.html.twig`), **every one of these 9 `.on('click', ...)` handlers binds to an empty jQuery selection and silently does nothing.** No console error — this is why the bug is so easy to miss.

2. **The custom `$(document).ready(...)` script at the bottom of the file** (hand-written, not minified). This uses the **globally exposed** `window.prestashop.component.Grid` / `window.prestashop.component.GridExtensions.*` — a separate library from the one bundled privately above — to create a **second** Grid wrapper on the same container and add **only the extras that are NOT already in the private bootstrap**, typically:
   - `AsyncToggleColumnExtension` (for `ToggleColumn` AJAX toggling)
   - `PositionExtension` (for `PositionColumn` drag-and-drop)

   **Do NOT re-add `SortableColumnExtension`/`SortingExtension` or `ResetSearchExtension`/`FiltersResetExtension` here just to "make sort/reset work"** — the private bootstrap in block 1 already binds those; if sort/reset don't work, fix the ID in block 1 instead of duplicating extensions in block 2. The one documented exception is `PositionExtension` + `ReorderPositionsButtonType`: the "Rearrange" button simulates a `.click()` on `.ps-sortable-column`, so a `SortingExtension`/`SortableColumnExtension` click handler must exist for that simulated click to do anything — see the gotcha below.

### Search (the search button, not sort)

Search is a **plain HTML form POST**, not AJAX — clicking "Search" submits `grid.filter_form` to whatever route the browser is currently on (the index route, since `form_start` doesn't override `action`). This means:
- The **search route MUST share the same path as the index route**, only `methods: [POST]` differs (see routes.yml section above) — otherwise 405.
- `searchAction()`'s **third argument to `buildSearchResponse()` must be the literal `GRID_ID` string** (e.g. `'featuredcategoryproducts'` or `YourFactory::GRID_ID`), **never** a `Filters::class` name. Passing the wrong type doesn't throw immediately but the search silently fails to persist filters / just reloads the page with no results applied.

### Quick diagnosis checklist when sort/reset/search "does nothing"

1. `grep -o '"YOUR_GRID_ID"' views/js/{modulename}.bundle.js` — must find the ID **inside the minified bootstrap**, not just in the bottom custom script. If it's missing there, that's the bug.
2. Confirm the DOM container id: view page source, search for `id="..._grid"` — it must equal `{GRID_ID}_grid`.
3. `searchAction()` third param must be the `GRID_ID` string, not a class reference.
4. Column `sortable` option — **defaults to `true`** in `AbstractColumn::configureOptions()`. You almost never need to set it explicitly; if sort still fails after fixing the ID, this is NOT the cause.

---

## Key gotchas

- `getFilters()` return type must be **`FilterCollectionInterface`** (not `FilterCollection`) — PHPStan enforces this.
- `getGridActions()` return type must be **`GridActionCollectionInterface`** (not `GridActionCollection`) — same rule.
- **Grid bundle must be loaded ONLY in the Twig `{% block javascripts %}`** — never also in `hookDisplayBackOfficeHeader`. Loading twice registers `AsyncToggleColumnExtension` twice: each click fires two AJAX calls that cancel each other out, leaving the DB unchanged while the UI shows success. This is silent and very hard to debug.
- **`SortingExtension` is mandatory when using `PositionColumn` with `ReorderPositionsButtonType`** — `PositionExtension` toggles reorder-mode by simulating a `.click()` on the `.ps-sortable-column` header. Without `SortingExtension`, no click handler exists on those headers and the click is a no-op. Symptom: "Done/Rearrange" button appears to do nothing when clicked. See the `$(document).ready` in `scripts/grid.bundle.js` for the correct extension order.
- **`FiltersResetExtension` is mandatory for the reset search button** — the reset button has `type="reset"` (clears the HTML form) but also needs a POST to the session-clear route via `data-url`. Without `FiltersResetExtension` the click handler is not registered and clicking Reset only clears the form fields in the browser without actually clearing the stored session filters.
- `ToggleColumn` fires AJAX POST with the route param from `route_param_name` — the controller method **must accept that param by the same name** (e.g. `int $entityId`).
- `PositionColumn` POSTs a `positions[]` array to `update_route` — the controller **must** read it via `$request->request->all()['positions'] ?? []`, NOT `$request->request->get('positions')`. Symfony's `InputBag::get()` throws `BadRequestException: Input value "positions" contains a non-scalar value.` when the value is an array.
- `DoctrineGridDataFactory` 4th argument is a **string hook identifier** matching your GRID_ID value — not a service reference.
- `getContextListShopID()[0]` in services.yml gets the single current shop ID (integer) required by the query builder.
- `index.php` guards must exist in **all** Grid subdirectories — lotr adds them automatically.
- **NEVER start module route paths with `/modules/`** — `YamlModuleLoader` always prepends `/modules` automatically. Path `/modules/mymodule/...` becomes `/modules/modules/mymodule/...`, causing 404/405 on every action. Use `/mymodule/...` instead.
- **Index (GET) and search (POST) MUST share the same path** — the Grid search form POSTs to the current page URL (the index URL). If the search route has a different path (e.g. `/entities/search`), the POST hits the index route which only accepts GET → 405 Method Not Allowed.
- **Bundle webpack Grid ID must match `GRID_ID` constant** — if you copy a bundle from another module, the minified section still contains the old grid ID **as a real literal string, not `GRID_ID_PLACEHOLDER`**, so a naive sed replace of the placeholder finds nothing. Replace every occurrence with the actual grid ID and verify with `grep -c`. Mismatch means row links, bulk actions, search reset, and column sort silently fail. See "How sort, search and reset actually work" above for the full mechanism.
- **`searchAction()`'s 3rd arg to `buildSearchResponse()` must be the `GRID_ID` string, not `YourFilters::class`** — passing the Filters class name instead of the grid ID string makes search silently do nothing (page just reloads, no filters applied).
- **Column `sortable` option already defaults to `true`** (`AbstractColumn::configureOptions()`) — do not waste time explicitly setting `'sortable' => true` on `DataColumn`s when debugging broken sort; the real cause is almost always the bundle ID mismatch above, not the column definition.
- **`ImageColumn` always renders `<img src="...">` unconditionally** — if the `src_field` value is empty/null the browser shows a broken image icon. Fix: (1) make the SQL return `NULL` (not empty string) when there is no image using `IF(photo IS NOT NULL AND photo != '', CONCAT(base_url, photo), NULL)`; (2) create a custom Twig template that guards with `{% if record[...] is not empty %}`; (3) register the module views dir under the `@PrestaShop` Twig namespace in `services.yml` and name the template `{gridId}_{columnId}_{columnType}.html.twig` — `GridExtension::getTemplatePath` checks that path first. See the "ImageColumn custom template" section below.
- **`ToggleColumn` for boolean grid columns** — always pair with a `YesAndNoChoiceType` filter. Use `ToggleColumn` (not `DataColumn`) for any `active`/boolean field. Add `YesAndNoChoiceType` filter with `setTypeOptions(['required' => false])`. The controller toggle action returns JSON `{status: bool, message: string}`. The `primary_field` option must point to the PK field name in the SELECT result. See the "ToggleColumn and boolean filters" section below.

---

## Position column and drag-and-drop — complete reference

### How it works end-to-end

1. `PositionColumn` is defined in `GridDefinitionFactory` with type `'position'`.
2. `GridPresenter::getColumns()` checks `searchCriteria->getOrderBy()`. **Only when the grid is currently sorted by `position`** does it prepend a synthetic `position_handle` column (type `'position_handle'`) at the start of the column list.
3. The `position_handle` Twig template (`@PrestaShop/Admin/Common/Grid/Columns/Content/position_handle.html.twig`) renders a `<div class="position-drag-handle js-{GRID_ID}-position">` with data attributes for ID, position, update URL and method.
4. `PositionExtension` (loaded by `wsfaq.bundle.js`) calls `tableDnD` on the grid table using `.js-drag-handle` as the drag handle. On drop it reads each row's data, computes old/new positions, and POSTs `positions[i][rowId]`, `positions[i][oldPosition]`, `positions[i][newPosition]` to the `update_route`.
5. `updatePositionAction` reads these via `$request->request->all()['positions']` and delegates to `GridPositionUpdaterInterface`.

### CSS: drag handle is only visible when sorted by position

```css
/* From PS theme.css — drag handle hidden by default, shown on hover only when grid-ordering-column class is present */
table.grid-ordering-column tr:hover .position-drag-handle { visibility: visible }
```

The `grid-ordering-column` class is added to the `<table>` by the Twig template only when `is_ordering_column(grid)` returns true — which itself checks that the current `orderBy` equals the `PositionColumn`'s id. **If the grid is sorted by any other column, the class is absent and no drag handle appears.**

### CRITICAL: drag-and-drop breaks when sorted or filtered by a non-position column

Drag-and-drop works in two situations:
1. **Initial state** — no sort in the URL. `Filters::getDefaults()` sets `'orderBy' => 'position'`, so `GridPresenter` sees `orderBy === 'position'` and injects the `position_handle` column.
2. **Explicitly sorted by Position** — user clicked the Position column header.

Drag-and-drop is **disabled** (the `position_handle` column is not rendered at all) when:
- The user clicks any other column header (e.g. Name, Active…), adding an `[orderBy]=name` param to the URL.
- The user applies a text filter on another column — the resulting redirect also carries a non-position `orderBy`.

URL when sorted by name (drag disabled):
```
?wsfaq_question%5BorderBy%5D=name&wsfaq_question%5BsortOrder%5D=asc
```

To re-enable drag-and-drop: click the **"Position"** column header to return to position sort. You can also tell the user: **"Drag-and-drop only works when the list is not sorted by another column. Click the Position column header (or reset filters) to re-enable it."**

**The proper UX solution:** add a `ReorderPositionsButtonType` filter for the `position` column. This renders a **"Rearrange"** button in the filter row. Clicking it resets the sort to `position` ASC and makes drag-and-drop available again immediately — no need for the user to click the column header.

```php
use PrestaShopBundle\Form\Admin\Type\ReorderPositionsButtonType;

->add((new Filter('position', ReorderPositionsButtonType::class))
    ->setAssociatedColumn('position')
)
```

This filter takes no `setTypeOptions()` — just the class and `setAssociatedColumn('position')`. Always include it whenever you declare a `PositionColumn`.

### Filters::getDefaults() — must default to `'orderBy' => 'position'`

```php
public static function getDefaults(): array
{
    return [
        'limit'     => 20,
        'offset'    => 0,
        'orderBy'   => 'position',   // REQUIRED — enables drag-and-drop on first load
        'sortOrder' => 'asc',
        'filters'   => [],
    ];
}
```

### PositionColumn options

```php
(new PositionColumn('position'))           // column ID must be 'position'
    ->setName($this->trans('Position', [], 'Admin.Global'))
    ->setOptions([
        'id_field'             => 'id_myentity',   // PK field name in the SELECT result
        'position_field'       => 'position',       // position field name in SELECT result
        'update_method'        => 'POST',
        'update_route'         => 'mymodule_myentity_update_position',
        'record_route_params'  => [
            'id_myentity' => 'entityId',  // maps SELECT field → route param name
        ],
    ])
```

### QueryBuilder must SELECT position

The `position` field must be in the `SELECT`. The `position_handle` template reads `record[column.options.position_field]`, so if `position` is absent from the query result the drag handle will render with empty data attributes and the drop handler will break silently.

```php
$qb->select(
    'e.id_myentity',
    'e.position',      // REQUIRED — used by position_handle template
    'e.active',
    'el.name'
);
```

### PositionDefinition in services.yml

```yaml
mymodule.grid.position_definition:
  class: 'PrestaShop\PrestaShop\Core\Grid\Position\PositionDefinition'
  arguments:
    $table:         'prefix_mymodule_items'   # WITHOUT DB prefix — handler adds it at runtime
    $idField:       'id_myentity'
    $positionField: 'position'
```

### updatePositionAction — read positions array correctly

```php
// CORRECT — InputBag::get() throws BadRequestException on array values
$positionsData = ['positions' => $request->request->all()['positions'] ?? []];

// WRONG — throws: Input value "positions" contains a non-scalar value
$positionsData = ['positions' => $request->request->get('positions')];
```

### Replying to users about drag not working

If a user reports that drag-and-drop stopped working or the drag handle is missing:

1. **Check the URL** — if `%5BorderBy%5D=name` (or any column other than `position`) is present in the URL, the grid is sorted by that column and drag is intentionally disabled by PS.
2. **Fix**: click the "Position" column header to sort by position → drag-and-drop reactivates.
3. **Check disk quota** — if `var/cache/` cannot be written (errno=122, Disk quota exceeded), the Twig cache is stale. Clean `var/cache/dev/` to free space, then reinstall the module so the cache rebuilds.
4. **Check the bundle Grid ID** — if you recently copied or renamed the bundle, verify both occurrences of the Grid ID inside `wsfaq.bundle.js` match `QuestionGridDefinitionFactory::GRID_ID` exactly.

---

## ImageColumn custom template — no broken image when src is null

`ImageColumn` uses the PS core template `@PrestaShop/Admin/Common/Grid/Columns/Content/image.html.twig` which renders `<img src="...">` unconditionally — if the value is empty/null the browser shows a broken image icon.

**Full fix (3 steps):**

**Step 1 — SQL returns NULL when no image:**
```php
// BAD: always produces a URL even with empty photo
"CONCAT('" . __PS_BASE_URI__ . "modules/mymodule/upload/', COALESCE(photo, '')) AS photo_src"

// GOOD: NULL when no photo
"IF(photo IS NOT NULL AND photo != '', CONCAT('" . __PS_BASE_URI__ . "modules/mymodule/upload/', photo), NULL) AS photo_src"
```

**Step 2 — Custom Twig template with null guard:**

Create `views/PrestaShop/Admin/Common/Grid/Columns/Content/{gridId}_{columnId}_image.html.twig`:
```twig
{% if record[column.options.src_field] is not empty %}
    <img src="{{ record[column.options.src_field] }}" style="max-height:40px;" />
{% endif %}
```
Filename pattern: `{GRID_ID}_{column_id}_image.html.twig` (e.g. `wsfaq_question_photo_src_image.html.twig`).

**Step 3 — Register module views dir under `@PrestaShop` Twig namespace in `services.yml`:**
```yaml
twig.loader.filesystem:
  calls:
    - [addPath, ['%kernel.project_dir%/modules/mymodule/views/PrestaShop', 'PrestaShop']]
```

`GridExtension::getTemplatePath` checks templates in this order:
1. `@PrestaShop/.../{gridId}_{columnId}_{type}.html.twig` ← **custom template found here first**
2. `@PrestaShop/.../{gridId}_{type}.html.twig`
3. `@PrestaShop/.../{type}.html.twig` ← core fallback

This override is grid+column specific — no other PS grid is affected.

**NEVER** put uploads inside `views/` — the `views/` folder is for Twig templates only. User-uploaded files must go in a dedicated directory at module root (e.g. `upload/`, `images/`, `files/`) with a proper `.htaccess`. The `views/PrestaShop/` subtree added above is only for template overrides, not for file storage.

---

## ToggleColumn and boolean filters — complete pattern

### ToggleColumn declaration

```php
(new ToggleColumn('active'))
    ->setName($this->trans('Active', [], 'Admin.Global'))
    ->setOptions([
        'field'           => 'active',        // field name in SELECT result
        'primary_field'   => 'id_myentity',   // PK field name in SELECT result
        'route'           => 'mymodule_myentity_toggle_status',
        'route_param_name' => 'entityId',     // name used in route + controller arg
    ])
```

### YesAndNoChoiceType filter (always pair with ToggleColumn)

```php
use PrestaShopBundle\Form\Admin\Type\YesAndNoChoiceType;

->add((new Filter('active', YesAndNoChoiceType::class))
    ->setTypeOptions(['required' => false])
    ->setAssociatedColumn('active')
)
```

- No `attr` / `placeholder` needed — `YesAndNoChoiceType` renders a native `<select>` with "---", "Yes", "No".
- The `setAssociatedColumn` value must match the column ID **and** the field name used in `getFilters()` of the `QueryBuilder`.

### Toggle controller action

```php
public function toggleStatus(Request $request, int $entityId): Response
{
    // load entity by $entityId, flip ->active, save
    return $this->json([
        'status'  => true,
        'message' => $this->trans('The status has been successfully updated.', 'Admin.Notifications.Success', []),
    ]);
}
```

The route param name (`entityId` here) **must match** both `route_param_name` in `ToggleColumn` options and the controller method argument name.

### QueryBuilder: filter active by boolean value

```php
if (isset($filters['active']) && $filters['active'] !== '') {
    $qb->andWhere('e.active = :active')
       ->setParameter('active', (int) $filters['active']);
}
```
