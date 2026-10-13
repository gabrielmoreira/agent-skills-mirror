# Test Data Setup

## Prefer SQL fixture files

Put reusable database fixtures in `src/test/resources/test-data.sql` and run them
with Spring's `@Sql("classpath:/test-data.sql")`. Apply the annotation at class
level to set up data before every test method, or at method level for a fixture
specific to that test.

```java
import org.springframework.test.context.jdbc.Sql;

@Sql("classpath:/test-data.sql")
class ProductIntegrationTest extends BaseIT {
    // Each test method starts with the SQL fixture loaded.
}
```

The default execution phase is `BEFORE_TEST_METHOD`; do not switch to
`BEFORE_TEST_CLASS` for fixtures that must be loaded for every test. Method-level
`@Sql` overrides class-level declarations by default, so include the shared
fixture in the method's scripts or use `@SqlMergeMode(MERGE)` when both are needed.

Keep fixtures deterministic and independent of test execution order. Use test
transaction rollback where it applies; for tests without rollback, reset data
in the setup script or use a cleanup script with
`@Sql(scripts = "classpath:/cleanup.sql", executionPhase = Sql.ExecutionPhase.AFTER_TEST_METHOD)`.

## Prefer exposed Services or ModuleAPI classes for programmatic setup

When fixtures need to be created programmatically, use exposed Services or
ModuleAPI classes instead of Repositories, `JdbcTemplate`, or `JdbcClient`.
Create data through the application's supported operations so setup respects
business rules and module boundaries rather than depending on persistence internals.

## Avoid inline SQL and manual transaction plumbing

Unless absolutely necessary, do not use `JdbcTemplate`, `JdbcClient`, or
`TransactionTemplate` to set up test data by executing SQL statements. This couples
tests to internal implementation details and scatters fixture SQL through Java code.
Prefer SQL files executed by `@Sql`, or exposed Services or ModuleAPI classes.

If a persistence-specific scenario cannot be expressed through either preferred
approach, keep the exception narrowly scoped and explain why it is necessary.
Distinguish fixture setup from exercising a repository or JDBC operation that is
itself the behavior under test.

Source: [Spring Framework — Executing SQL scripts](https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/executing-sql.html).
