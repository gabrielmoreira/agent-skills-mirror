# AEM Frontend Build Pipeline

## Purpose
Implement modern frontend build pipelines for AEM including webpack/Vite configuration, client library generation, CSS/JS optimization, and integration with AEM's ui.frontend module architecture.

## When to Use (Triggers)
- User mentions "frontend build," "webpack," "client libraries," or "ui.frontend"
- References to npm, CSS compilation (SASS/LESS), or JavaScript bundling
- Questions about clientlib generation, code splitting, or asset optimization
- Requests involving SPA frameworks (React/Angular/Vue) with AEM integration
- Discussion of frontend development workflow, hot reload, or proxy configuration

## Core Capabilities
- Configure webpack/Vite for AEM clientlib generation via aem-clientlib-generator
- Implement CSS preprocessor pipelines (SASS/LESS) with PostCSS optimization
- Set up JavaScript bundling with tree-shaking and code splitting
- Configure frontend proxy development workflow with AEM backend
- Integrate SPA frameworks with AEM SPA Editor SDK

## Domain Knowledge Required
### Technical Foundation
- Module bundlers (webpack 5, Vite, Rollup) and their configuration
- CSS preprocessors (SASS, LESS) and PostCSS plugin ecosystem
- JavaScript module systems (ESM, CommonJS) and code splitting strategies
- Node.js/npm project management and dependency resolution

### AEM-Specific Context
- AEM Client Library (clientlib) structure (js.txt, css.txt, categories)
- `aem-clientlib-generator` npm package for automated clientlib creation
- AEM Archetype ui.frontend module structure and build integration
- SPA Editor SDK (React, Angular) and its build requirements
- Component-scoped styles vs. global theme clientlibs
- Client library dependencies and embed patterns

## Implementation Approach
### Step 1: Project Structure
Set up the frontend module within AEM project.
- Initialize ui.frontend module following AEM Archetype patterns
- Configure package.json with build scripts (dev, prod, watch)
- Set up source directory structure (components, themes, utilities)
- Define clientlib output categories aligned with page structure

### Step 2: Build Configuration
Configure the bundler for AEM-compatible output.
- Set up webpack/Vite with appropriate entry points per clientlib category
- Configure aem-clientlib-generator for automated clientlib creation
- Set up CSS extraction and optimization (MiniCssExtractPlugin / Vite CSS)
- Configure asset handling (fonts, images, SVGs) with correct paths

### Step 3: Development Workflow
Enable rapid frontend iteration.
- Configure webpack-dev-server / Vite dev server with AEM proxy
- Set up hot module replacement (HMR) for CSS and JS changes
- Configure source maps for debugging in AEM context
- Implement BrowserSync or similar for multi-device testing

### Step 4: Optimization
Apply production optimizations to build output.
- Configure tree-shaking for unused code elimination
- Implement code splitting for route-based or component-based chunks
- Set up CSS optimization (purging, minification, autoprefixer)
- Configure long-term caching with content hashing

### Step 5: CI/CD Integration
Integrate frontend build into deployment pipeline.
- Configure Maven build to trigger npm build via frontend-maven-plugin
- Set up Node.js version management in CI environment
- Implement build caching for faster CI runs
- Configure environment-specific builds (dev, stage, prod)

## Quality Checklist
- [ ] Production build outputs optimized, minified bundles
- [ ] Source maps available for debugging but not shipped to CDN
- [ ] Client library categories correctly mapped to page regions
- [ ] No JavaScript errors in browser console on any page template
- [ ] CSS doesn't conflict between components (scoped or namespaced)
- [ ] Build time under 60 seconds for full production build
- [ ] Hot reload works for both CSS and JS changes in development
- [ ] Bundle size within budget (< 200KB JS gzipped for initial load)

## Related Skills
- aem-component-development (frontend of components)
- aem-caching-strategy (clientlib caching with fingerprinting)
- aem-performance-tuning-profiling (frontend performance measurement)

## Example Use Cases
1. **Design System Integration:** Implement a shared design system (Storybook-based) that compiles into AEM clientlibs, enabling component development outside AEM with seamless integration via the build pipeline.
2. **SPA Migration:** Convert traditional AEM site to React SPA using AEM SPA Editor SDK, configuring webpack for both SPA Editor-compatible builds and standalone development mode with mock data.
3. **Micro-Frontend Architecture:** Implement Module Federation (webpack 5) for independently deployable frontend features within AEM, enabling different teams to deploy frontend changes without full site rebuild.

## Notes
- `frontend-maven-plugin` downloads and manages Node.js — don't require global Node installation for builds
- Client library categories determine loading order — plan categories carefully to avoid blocking rendering
- AEM Cloud Service supports the same frontend build patterns as on-premise
- Vite is gaining adoption for AEM frontend builds due to faster dev server and simpler configuration
