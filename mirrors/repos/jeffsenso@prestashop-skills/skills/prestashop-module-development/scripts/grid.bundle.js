/**
 * Copyright since 2009 Websenso
 *
 * This file is part of Websenso plugin for PrestaShop. See COPYING.md for license details
 * Websenso is a Digital Agency
 *
 * This file is licenced under the Academic Free License 3.0 (AFL-3.0).
 * With the purchase or the installation of the software in your application
 * you accept the licence agreement
 *
 * @author    Websenso <bonjour@websenso.com> (https://www.websenso.com)
 * @copyright Since 2009 Websenso
 * @license   https://opensource.org/licenses/afl-3.0.php Academic Free License (AFL 3.0)
 */

/**
 * PrestaShop Grid initialisation for module admin pages — copy as views/js/{modulename}.bundle.js, no edit needed.
 *
 * Uses the core Grid component and extensions exposed by the back office main bundle on
 * window.prestashop.component (the same API as core pages, e.g. Improve > Design > Pages):
 * maintained by PrestaShop, no minified copy in the module, no grid ID to replace.
 *
 * Every grid of the page is initialised automatically: the core template grid.html.twig renders
 * <div class="js-grid" id="{grid_id}_grid" data-grid-id="{grid_id}">, so single and multi-grid pages work alike.
 *
 * Load it ONCE, only from the Twig {% block javascripts %} (never also in hookDisplayBackOfficeHeader:
 * every extension would be bound twice, e.g. a toggle fires two AJAX calls that cancel each other).
 *
 * Must run in a jQuery ready callback, NOT on DOMContentLoaded: the admin theme creates
 * window.prestashop.component in its own $(() => initPrestashopComponents()) (new-theme/js/theme.ts), and jQuery 3
 * runs ready callbacks after DOMContentLoaded. This script is loaded after the theme bundle, so its ready
 * callback is queued after the theme's one and the components exist.
 *
 * Compatible with PrestaShop 8.0+ and 9.x: Grid, GridExtensions (all extensions used below) and the
 * $(() => initPrestashopComponents()) theme init are identical in 8.0.0, 8.1.0, 8.2.0 and 9.0.0 (checked in the
 * core sources). Tested live on PrestaShop 9.1.4. PositionExtension handles the "Rearrange" button
 * (.js-btn-reorder-positions) from 8.2 only; on 8.0 / 8.1 it is added through the .js-drag-handle check.
 */
window.jQuery(function () {
  'use strict';

  var component = window.prestashop && window.prestashop.component;
  if (!component || !component.Grid || !component.GridExtensions) {
    // eslint-disable-next-line no-console
    console.error('Grid: window.prestashop.component.Grid is not available, grid extensions not bound.');

    return;
  }

  var extensions = component.GridExtensions;

  document.querySelectorAll('.js-grid[data-grid-id]').forEach(function (container) {
    // Guard against a double inclusion of this script
    if (container.dataset.gridInitialized) {
      return;
    }
    container.dataset.gridInitialized = '1';

    var grid = new component.Grid(container.dataset.gridId);

    // Filters: Search button enabling and Reset (POST to the reset route, then redirect)
    grid.addExtension(new extensions.FiltersResetExtension());
    grid.addExtension(new extensions.FiltersSubmitButtonEnablerExtension());
    // Column header click => sort (page reload with {grid_id}[orderBy] / [sortOrder])
    grid.addExtension(new extensions.SortingExtension());
    // Grid actions: "Refresh list", "Show SQL query", "Export to SQL Manager"
    grid.addExtension(new extensions.ReloadListExtension());
    grid.addExtension(new extensions.ExportToSqlManagerExtension());
    grid.addExtension(new extensions.SubmitGridActionExtension());
    // Row actions: LinkRowAction (+ clickable_row) and SubmitRowAction (delete...)
    grid.addExtension(new extensions.LinkRowActionExtension());
    grid.addExtension(new extensions.SubmitRowActionExtension());
    // Bulk actions: checkboxes + submit
    grid.addExtension(new extensions.BulkActionCheckboxExtension());
    grid.addExtension(new extensions.SubmitBulkActionExtension());
    // ToggleColumn: AJAX toggle, the controller must return JSON {status, message}.
    // Never add ColumnTogglingExtension as well: both bind the same .ps-togglable-row switch.
    grid.addExtension(new extensions.AsyncToggleColumnExtension());

    // PositionColumn: drag-and-drop + "Rearrange" button (ReorderPositionsButtonType filter).
    // Only when the grid has one, PositionExtension always applies tableDnD to the table.
    if (container.querySelector('.js-btn-reorder-positions, .js-drag-handle')) {
      grid.addExtension(new extensions.PositionExtension(grid));
    }
  });
});
