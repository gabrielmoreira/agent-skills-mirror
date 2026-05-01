---
applyTo: "**/test/**/*Tests.cs"
---

# General Guidelines
- Use these frameworks: xUnit, Moq, FluentAssertions (existing tests), xUnit Asserts (new tests).
- For unit tests on Repository classes, use Squadron to create a MongoDB.
- If there are more than 5 asserts to do on a result, use Snapshooter instead.
- Use Theories instead of multiple tests.
- Never use [MemberData].

# Test Naming Conventions
- Test class names should end with "Tests" (e.g., UserServiceTests)
- Test method names should follow the pattern: MethodName_Scenario_ExpectedBehavior
- Use descriptive names that clearly indicate what is being tested
- Name the result in the Act part either `result` or `act` when testing for exceptions.

# Test Data and Setup
- Mocks: 
  Define as fields and instantiate directly if possible
  Pre-configure default behaviour in the constructor when appropriate
  Use MockBehavior.Strict as default
- Instantiate the class under test in the constructor of the test class
- Avoid creating the same test data repeatedly. Instead, use sample data classes.
- When using Squadron, ensure to re-use the instance by creating a collection fixture

# Test Structure
- Follow Arrange-Act-Assert (AAA) pattern in all tests
- Use separate lines or comments to clearly delineate AAA sections
- Keep tests focused on a single behavior or scenario
- Having no or few lines in the Arrange section is preferred.

# Assertions
- Use FluentAssertions for consistency reasons for existing tests
- Use xUnit Asserts in new tests

# Snapshot Testing
- Use Snapshooter when testing complex objects with many properties
- Update snapshots deliberately when behavior changes are intended
- Review snapshot changes carefully during code reviews

# Mocking and Dependencies
- Use clear, descriptive variable names for mocks
- Avoid defining mocks inside the test method when possible.
- Verify mock interactions when behavior verification is important
- When verifying mock interactions, avoid using It.IsAny<T>() if a more specific constraint can be used

# Error Handling and Exception Testing
- Test both happy path and error scenarios
- Use FluentAssertions for exception testing: .Should().ThrowExactly[Async]<ExceptionType>()
- Verify exception messages and properties when relevant
- Test error propagation in service layers
