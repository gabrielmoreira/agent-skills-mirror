---
name: ruby-patterns
description: "Extracts Ruby and Rails backends into service and query objects, thin controllers, pinned Bundler manifests, and includes/preload/eager_load N+1 strategy. Use when fat models, fat controllers, Gemfile drift, or N+1 loops are the work. Never a RSpec/Minitest cookbook (rails-testing) or a Brakeman/OWASP deep chair (ruby-security)."
version: 1.0.1
risk: safe
source: modernized
date_modernized: "2026-05-31"
tags:
  - ruby
  - rails
  - service-objects
  - bundler
  - database-queries
  - error-handling
tools:
  - gemini
  - codex
---

# Ruby and Rails Structural Design Patterns Guide

## When to Use

Use this skill when developing or reviewing backend service code written in Ruby. It applies when:

- Designing Ruby backends, console apps, or Rails web applications.
- Structuring business logic outside of standard Active Record models (e.g., Service Objects, Query Objects, Decorators).
- Configuring package dependencies using Bundler and managing Gemfile versions securely.
- Diagnosing database query anomalies (such as N+1 query loops) and structuring transactional boundaries.
- Reviewing controller layers for fat-controller anti-patterns or missing strong-parameter protections.
- Setting up exception-handling boundaries in API controllers or background job workers.

Trigger keywords: `service object`, `query object`, `thin controller`, `N+1`, `bundler`, `Gemfile`, `bundle-audit`, `brakeman`, `ActiveJob`, `Sidekiq`, `rescue_from`, `eager_load`, `preload`, `includes`, `strong parameters`, `SQL injection`, `fat model`.

## Prerequisites

- Ruby 3.x or later installed and available on PATH.
- Rails 7.x+ project with Bundler initialized (`Gemfile` and `Gemfile.lock` present).
- Windows host is primary (PowerShell). Use forward-slash paths inside Ruby code; use backslash or forward-slash paths in PowerShell commands as appropriate.
- `bundle-audit` and `brakeman` gems available for security scanning (install via `gem install bundle-audit brakeman` if not in Gemfile).
- Access to project directory (e.g., `~\projects\myapp`).

## Procedure

### 1. Restate the outcome and success criteria

Before writing code, restate in one sentence what the artifact will achieve (e.g., "Extract user-creation logic from the User model into a transactional Service Object with contextual error handling").

### 2. Inspect available context

- Review existing models, controllers, services, and background jobs before proposing changes.
- Identify missing or risky assumptions (e.g., does the app use Sidekiq or Solid Queue? Is PostgreSQL or MySQL the database?).
- Check current Rails and Ruby versions: `ruby -v` and `rails -v` (or `bundle exec rails -v`).

### 3. Enforce Single Responsibility and Domain Service Isolation

- **De-fat Models**: Extract business transactions from Rails ActiveRecord models into isolated Service Objects. Models must contain validations, relationships, and basic scopes only.
- **Short Methods**: Write short, intention-revealing methods. If a method exceeds 10 lines, abstract sub-routines into helper methods or specialized classes.
- **Query Objects**: Extract complex SQL queries or Active Record chains into separate Query Objects to keep model classes clean and testable.

Example Service Object pattern (`app/services/create_user_service.rb`):

```ruby
# app/services/create_user_service.rb
class CreateUserService
  class ValidationError < StandardError; end

  def initialize(params:)
    @params = params
  end

  def call
    # 1. Enforce validation boundaries
    raise ValidationError, "Email parameter is required" if @params[:email].blank?

    ActiveRecord::Base.transaction do
      # 2. Instantiate and save record
      user = User.new(@params)

      unless user.save
        raise ValidationError, user.errors.full_messages.join(', ')
      end

      # 3. Trigger background job with ID, not full object
      SendWelcomeEmailJob.perform_later(user.id)

      user
    end
  rescue ValidationError => e
    Rails.logger.warn("UserService failure: #{e.message}")
    raise e
  end
end
```

### 4. Configure exception-handling boundaries

- **Specific Rescue Clauses**: Never use bare `rescue` (which rescues `StandardError`) or `rescue Exception` (which captures system signals like SIGTERM). Always specialize (e.g., `rescue ActiveRecord::RecordNotFound`).
- **Raise with Context**: Pass meaningful diagnostic details into custom exceptions rather than raising plain strings.
- **Fail Fast**: Stop execution immediately when a validation or state pre-condition is violated.

Example API controller boundary (`app/controllers/api_controller.rb`):

```ruby
# app/controllers/api_controller.rb
class ApiController < ActionController::API
  rescue_from ActiveRecord::RecordNotFound, with: :handle_not_found
  rescue_from CreateUserService::ValidationError, with: :handle_validation_error

  private

  def handle_not_found(exception)
    render json: { error: 'Record not found', detail: exception.message }, status: :not_found
  end

  def handle_validation_error(exception)
    render json: { error: 'Validation failed', detail: exception.message }, status: :unprocessable_entity
  end
end
```

### 5. Manage dependencies with Bundler

- **Version Pinned Manifests**: Enforce strict version constraints for production gems inside the `Gemfile` (e.g., `gem 'pg', '~> 1.5'`).
- **Commit the Lockfile**: Always commit `Gemfile.lock` to source control to guarantee parity across local, staging, and production nodes.
- **Gem Auditing**: Scan dependencies regularly in the CI pipeline using `bundle-audit` or `brakeman`.

```powershell
# Install gems
bundle install

# Audit for known vulnerabilities
bundle-audit check

# Run static security analysis on the Rails app
brakeman
```

### 6. Apply Rails core best practices

- **Thin Controllers**: Controllers must only parse request parameters, call a single service object, and render or redirect. Zero business calculations in the controller layer.
- **Safe Background Jobs**: Ensure ActiveJob and Sidekiq tasks are idempotent (running multiple times yields the same state) and fail-safe, with automatic retry limitations configured.
- **Avoid N+1 Queries**: Eager-load database relationships using `.includes`, `.preload`, or `.eager_load` rather than lazily fetching associated rows in view loops.

### 7. Choose the correct query strategy

| Strategy | Method Call | SQL Execution Count | Best Use Case |
|----------|-------------|---------------------|---------------|
| **Lazy Loading** | `User.all` then `user.posts` | 1 + N queries | Tiny datasets where associations are not accessed in loops |
| **Includes** | `User.includes(:posts)` | 2 queries (usually) | General preloading where the agent might query or filter on associations |
| **Preload** | `User.preload(:posts)` | Exactly 2 queries | Fetching associations without referencing them in WHERE conditions |
| **Eager Load** | `User.eager_load(:posts)` | Exactly 1 query (LEFT OUTER JOIN) | Fetching records where association columns are used in filter queries |

### 8. Validate the result

- Check that no bare `rescue` or `rescue Exception` exists in the changed files.
- Confirm `Gemfile.lock` is committed if `Gemfile` changed.
- Run the test suite: `bundle exec rspec` or `bundle exec rails test`.
- Run `brakeman` and `bundle-audit check` on the final code.
- Verify no N+1 queries using `bullet` gem in development or by inspecting logs for repeated SELECT statements.

### 9. End with the next best move

Provide a concise Assumptions / Evidence / Risks / Next move section when the task is ambiguous or high impact. Include any rollback, review, or monitoring requirement.

## Examples

### Query Object pattern

```ruby
# app/queries/recent_active_users_query.rb
class RecentActiveUsersQuery
  def initialize(relation = User.all)
    @relation = relation
  end

  def call
    @relation
      .where(active: true)
      .where('last_sign_in_at > ?', 30.days.ago)
      .order(last_sign_in_at: :desc)
  end
end

# Usage in controller or service:
RecentActiveUsersQuery.new.call
```

### Pluck for lightweight attribute fetching

```ruby
# Slow — loads full ActiveRecord objects
User.all.map(&:email)

# Fast — returns array of strings
User.pluck(:email)
```

### Passing IDs to background jobs

```ruby
# Correct — pass primary key
SendWelcomeEmailJob.perform_later(user.id)

# Wrong — pass full object (state may change before job runs)
SendWelcomeEmailJob.perform_later(user)
```

## Pitfalls

- **Fat Models (God Objects)**: Bundling email dispatch, charge gateways, and file uploads directly inside ActiveRecord models, ballooning files to thousands of lines. Extract into Service Objects.
- **Blanket Rescue Blocks**: Writing `begin ... rescue => e ... end` without specifying the exception class, silently swallowing system errors and bugs. Always specify the exception class.
- **Bypassing Strong Parameters**: Directly feeding raw user inputs (`params[:user]`) into database writes, exposing the app to mass-assignment vulnerabilities. Always use `params.require(:user).permit(:name, :email, ...)`.
- **Rescuing `Exception`**: Rescuing the root `Exception` class instead of `StandardError` intercepts critical operating system signals (e.g., SIGTERM, SIGKILL), preventing web servers from shutting down cleanly. Never rescue `Exception`.
- **Dynamic SQL interpolation**: Using `User.where("name = '#{params[:name]}'")` bypasses Active Record parameter sanitization, opening the server to SQL Injection attacks. Always use parameterized queries: `User.where(name: params[:name])`.
- **Passing full objects to background jobs**: Database state can change before the job runs. Always pass primary key IDs and re-fetch the record inside the job.
- **Forgetting to commit `Gemfile.lock`**: Leads to dependency drift across environments. Always commit the lockfile alongside Gemfile changes.

## Verification

Run these commands to verify the skill's patterns are correctly applied:

```powershell
# Check Ruby and Rails versions
ruby -v
bundle exec rails -v

# Install dependencies
bundle install

# Run security audit
bundle-audit check

# Run static security analysis
brakeman

# Run test suite
bundle exec rspec
# or
bundle exec rails test

# Check for bare rescue statements in app code (PowerShell)
Select-String -Path "app\**\*.rb" -Pattern "rescue\s*$|rescue\s+Exception" -Recurse

# Check for N+1 query patterns in logs (look for repeated SELECT on associated tables)
# If using Bullet gem, check development logs for N+1 warnings
```

Expected outputs:
- `bundle-audit check`: "No vulnerabilities found" or lists vulnerabilities to address.
- `brakeman`: Summary report with 0 high-confidence warnings (or documented exceptions).
- `Select-String` for bare rescue: no matches in well-structured code.
- Test suite: all tests pass with no failures.

## Related skills

- `rails-testing` — RSpec and Minitest patterns for Rails service objects and controllers.
- `ruby-security` — Deeper Brakeman, bundle-audit, and OWASP coverage for Ruby applications.
- `sidekiq-patterns` — Idempotent job design, retry strategies, and dead-letter handling.

## Sources Checked (2026-05-31)

- Rails Guides — Active Record Querying: https://guides.rubyonrails.org/active_record_querying.html
- Rails Guides — Active Job: https://guides.rubyonrails.org/active_job_basics.html
- Bundler documentation: https://bundler.io/
- Brakeman documentation: https://brakemanscanner.org/
- OWASP API Security Top 10 2023: https://owasp.org/API-Security/editions/2023/en/0x00-header/
