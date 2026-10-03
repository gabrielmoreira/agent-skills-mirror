---
title: AngularJS
category: Framework and library
x-claim-provenance:
- claim: AngularJS support officially ended in January 2022.
  source: https://docs.angularjs.org/misc/version-support-status
- claim: Code the browser calls outside the AngularJS execution context modifies the model without AngularJS being aware until execution enters the context through $apply; AngularJS APIs such as $http, $timeout, and $interval do this implicitly, while custom event callbacks and third-party library callbacks need it explicitly; the $digest loop keeps iterating until the $evalAsync queue is empty and the $watch list detects no changes.
  source: https://github.com/angular/angular.js/blob/master/docs/content/guide/scope.ngdoc
- claim: The infdig error is thrown when the model becomes unstable and each $digest cycle triggers a state change and another cycle, past a maximum iteration count configured through $rootScopeProvider.
  source: https://github.com/angular/angular.js/blob/master/docs/content/error/$rootScope/infdig.ngdoc
- claim: Implicit annotation, which infers dependencies from parameter names, does not work with JavaScript minifiers or obfuscators because they rename parameters, and strict DI mode throws whenever a service uses implicit annotation.
  source: https://github.com/angular/angular.js/blob/master/docs/content/guide/di.ngdoc
---

AngularJS support officially ended in January 2022. The configured AngularJS version, module graph, annotation or minification strategy, routing, promise implementation, and third-party directive set decide which APIs and migration boundaries are available.

AngularJS notices model changes only through its digest. Code the browser calls outside the AngularJS execution context, such as a custom event callback or a third-party library callback, changes the model without AngularJS knowing until execution enters the context through `$apply`, which `$http`, `$timeout`, and `$interval` do on their own. The `$digest` loop then re-runs watchers until the model stops changing, and a model that never stabilizes exceeds the configured iteration limit and throws. Scope ownership, two-way binding, watcher scheduling, digest integration, directive compile and link behavior, transclusion, HTTP interceptors, and form validation are observable responsibilities rather than implementation details, and an extra digest or timeout can mask an ownership defect rather than repair it.

Dependencies inferred from parameter names do not survive minification, because minifiers rename the parameters, and strict DI mode makes every such implicit annotation throw, so code that works unminified can fail once minified unless every injectable is explicitly annotated.

Control flow, lifecycle, and ownership run through scope inheritance, watchers, digest and apply entry points, promise callbacks, timeouts used for ordering, directive lifecycle, transclusion, filters, HTTP transforms, route teardown, and DOM handlers. Subscriptions, handlers, watchers, and plugin state need explicit destruction. Behavior is also referenced indirectly, so moving or renaming it can break:

- string-named injections and annotation output
- root-scope broadcasts, delegated handlers, and inline event attributes
- load-time plugins and trusted HTML
- global functions

While AngularJS coexists with another framework, change detection, shared state, and URL routing each need a single owner. Wrappers, bootstrap bridges, and global services are explicit transition boundaries, and a remaining hybrid bootstrap means the migration has not finished.

Behavioral evidence covers injection, minified builds, scope inheritance, binding updates, digest timing, directives, transclusion, forms, routes, HTTP interception, promise completion, accessibility state, and teardown. The configured test harness with explicit digest or async helpers exercises AngularJS lifecycle as it actually runs, and lifecycle assumptions carried over from successor frameworks do not hold here. Performance evidence includes watcher count, digest frequency and duration, and DOM work under the real interaction, and an optimization must preserve binding correctness and destroy-time cleanup.
