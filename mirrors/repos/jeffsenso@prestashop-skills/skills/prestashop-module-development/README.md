# PrestaShop Module Development Skill

Complete AI-assisted workflow for modern PrestaShop 8.x/9.x module development using Symfony architecture and best practices.

## Overview

This skill provides comprehensive guidance for developing PrestaShop modules with modern patterns, including:

- **Modern architecture**: Symfony controllers, services, dependency injection, and Doctrine entities
- **Complete workflows**: From project setup to validation and debugging
- **Cart rules & vouchers**: Programmatic creation and management
- **Grid system**: CRUD list pages with filters, sorting, drag-and-drop positioning
- **Console commands**: Background tasks and batch operations
- **Security**: CSRF protection, SQL injection prevention, input validation
- **Translations**: Multilingual support with the new translation system
- **Legacy migration**: Convert HelperForm, ObjectModel, and jQuery patterns to modern equivalents
- **Theme integration**: Template injection, hooks, and front office widgets

## Key Features

### References Library
17 comprehensive reference documents covering:
- Module structure & installer patterns
- Configuration pages with Symfony forms
- Database operations & Doctrine entities
- Services architecture & dependency injection
- Grid system with drag-and-drop
- Cart rules & promotional vouchers
- Console commands
- Theme template injection
- Security best practices
- Debugging & troubleshooting

### Scripts & Tooling
- Pre-built JS bundles for Grid and translatable forms
- Validation tooling (lotr) for code quality
- PS9 core documentation integration

### Best Practices Enforcement
- No legacy static calls (`Context::getContext()`, `Configuration::get()`)
- Service-oriented architecture with proper DI
- Doctrine ORM for translatable entities
- Component-based service organization
- Symfony best practices for service visibility

## Quick Start

1. **Read SKILL.md** - Main entry point with workflow overview
2. **Use references/** - Detailed implementation guides for specific features
3. **Run validation** - Always validate with `lotr` and install test
4. **Check debugging.md** - Troubleshoot common issues

## Recent Updates

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

Latest features:
- Cart rules & vouchers reference (June 2026)
- Symfony console commands guide
- Order entity LoggableInterface implementation
- Theme template injection patterns
- Fixtures installer with raw SQL patterns
- Service visibility best practices

## Usage Context

Invoke this skill when:
- Creating new PrestaShop modules from scratch
- Modernizing legacy modules to Symfony architecture
- Implementing specific features (cart rules, grid lists, console commands)
- Troubleshooting module installation or runtime issues
- Converting legacy patterns (HelperForm, ObjectModel) to modern equivalents

## Validation

All code must pass:
1. **lotr** - Automated code quality checks (phpstan, phpcs, rector)
2. **Install test** - `php bin/console pr:mo install mymodule`

## Support

For issues or questions, refer to `references/debugging.md` for symptom/cause/fix tables covering all common failure modes.
