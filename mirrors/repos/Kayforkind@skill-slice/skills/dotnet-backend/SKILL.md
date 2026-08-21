---
name: dotnet-backend
description: "Implements ASP.NET Core 8+ services: Minimal or controller APIs, EF Core DbContext and migrations, JWT/Identity, hosted BackgroundService workers, exception middleware, health checks, and OpenAPI. Use for C# Web API, auth, or EF query reliability. Not a .NET Framework 4.x playbook; do not use as the Azure/AWS/GCP topology guide."
version: 1.0.1
risk: safe
source: self
date_added: "2026-02-27"
---

# .NET Backend Agent — ASP.NET Core & Enterprise API Expert

You are an expert .NET/C# backend developer building enterprise-grade APIs and services on ASP.NET Core 8+.

## When to Use

Use this skill when the user asks to:

- Build or refactor ASP.NET Core APIs (controller-based or Minimal APIs)
- Implement authentication/authorization in a .NET backend (JWT, Identity, OAuth, Azure AD)
- Design or optimize EF Core data access patterns (migrations, queries, tracking)
- Add background workers, scheduled jobs, or integration services in C#
- Improve reliability or performance of a .NET backend service
- Wire up validation, logging, health checks, or OpenAPI/Swagger

Trigger keywords: `ASP.NET Core`, `.NET`, `C#`, `EF Core`, `Entity Framework`, `Minimal API`, `Web API`, `JWT`, `Identity`, `Hangfire`, `SignalR`, `DbContext`, `migration`, `background service`, `MediatR`, `Serilog`.

## Prerequisites

- **.NET SDK 8.0+** installed and on PATH. Verify: `dotnet --version`
- **EF Core CLI tool** (optional but recommended): `dotnet tool install --global dotnet-ef`
- **Database provider** NuGet packages appropriate to the target (e.g., `Npgsql.EntityFrameworkCore.PostgreSQL`, `Microsoft.EntityFrameworkCore.SqlServer`, `Pomelo.EntityFrameworkCore.MySql`).
- **Windows host is primary** — commands below assume PowerShell. On macOS/Linux, adjust path separators and use `export` instead of `$env:`.
- **User Secrets** for local development (never commit live connection strings or JWT keys):
  ```powershell
  dotnet user-secrets init
  dotnet user-secrets set "ConnectionStrings:DefaultConnection" "YOUR_CONNECTION_STRING"
  dotnet user-secrets set "Jwt:Key" "YOUR_KEY"
  dotnet user-secrets set "Jwt:Issuer" "YOUR_ISSUER"
  dotnet user-secrets set "Jwt:Audience" "YOUR_AUDIENCE"
  ```

## Procedure

### 1. Scaffold or open the project

```powershell
# New Minimal API project
dotnet new web -n MyApp -o src/MyApp

# New controller-based Web API
dotnet new webapi -n MyApp -o src/MyApp --use-controllers

cd src/MyApp
```

Install core packages:

```powershell
dotnet add package Microsoft.EntityFrameworkCore --version 8.0.*
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL --version 8.0.*
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer --version 8.0.*
dotnet add package Swashbuckle.AspNetCore
dotnet add package Serilog.AspNetCore
dotnet add package FluentValidation.AspNetCore
```

### 2. Configure DbContext (code-first)

```csharp
// Data/AppDbContext.cs
using Microsoft.EntityFrameworkCore;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<PendingEmail> PendingEmails => Set<PendingEmail>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(e =>
        {
            e.HasIndex(u => u.Email).IsUnique();
            e.Property(u => u.Email).IsRequired().HasMaxLength(256);
        });
        base.OnModelCreating(modelBuilder);
    }
}
```

Register in `Program.cs`:

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
```

Create and apply migrations:

```powershell
dotnet ef migrations add InitialCreate
dotnet ef database update
```

### 3. Build API endpoints

**Minimal API pattern:**

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddAuthentication().AddJwtBearer();
builder.Services.AddAuthorization();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();
app.UseAuthentication();
app.UseAuthorization();

app.MapPost("/api/users", async (CreateUserRequest request, AppDbContext db, CancellationToken ct) =>
{
    if (string.IsNullOrEmpty(request.Email))
        return Results.BadRequest("Email is required");

    var hashedPassword = BCrypt.Net.BCrypt.HashPassword(request.Password);

    var user = new User
    {
        Email = request.Email,
        PasswordHash = hashedPassword,
        Name = request.Name
    };

    db.Users.Add(user);
    await db.SaveChangesAsync(ct);

    return Results.Created($"/api/users/{user.Id}", new UserResponse(user.Id, user.Email, user.Name));
})
.WithName("CreateUser")
.WithOpenApi();

app.Run();

record CreateUserRequest(string Email, string Password, string Name);
record UserResponse(int Id, string Email, string Name);
```

**Controller-based pattern:**

```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly AppDbContext _db;
    private readonly ILogger<UsersController> _logger;

    public UsersController(AppDbContext db, ILogger<UsersController> logger)
    {
        _db = db;
        _logger = logger;
    }

    [HttpGet]
    public async Task<ActionResult<List<UserDto>>> GetUsers(CancellationToken ct)
    {
        var users = await _db.Users
            .AsNoTracking()
            .Select(u => new UserDto(u.Id, u.Email, u.Name))
            .ToListAsync(ct);

        return Ok(users);
    }

    [HttpPost]
    public async Task<ActionResult<UserDto>> CreateUser(CreateUserDto dto, CancellationToken ct)
    {
        var user = new User
        {
            Email = dto.Email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(dto.Password),
            Name = dto.Name
        };

        _db.Users.Add(user);
        await _db.SaveChangesAsync(ct);

        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, new UserDto(user.Id, user.Email, user.Name));
    }
}
```

### 4. Add JWT authentication

```csharp
// Services/TokenService.cs
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

public class TokenService
{
    private readonly IConfiguration _config;

    public TokenService(IConfiguration config) => _config = config;

    public string GenerateToken(User user)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:Key"]!));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Name, user.Name)
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddHours(1),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
```

Register JWT in `Program.cs`:

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });
```

### 5. Add a background service

```csharp
// Services/EmailSenderService.cs
public class EmailSenderService : BackgroundService
{
    private readonly ILogger<EmailSenderService> _logger;
    private readonly IServiceProvider _services;

    public EmailSenderService(ILogger<EmailSenderService> logger, IServiceProvider services)
    {
        _logger = logger;
        _services = services;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _services.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            var pendingEmails = await db.PendingEmails
                .Where(e => !e.Sent)
                .Take(10)
                .ToListAsync(stoppingToken);

            foreach (var email in pendingEmails)
            {
                await SendEmailAsync(email);
                email.Sent = true;
            }

            await db.SaveChangesAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }

    private async Task SendEmailAsync(PendingEmail email)
    {
        _logger.LogInformation("Sending email to {Email}", email.To);
    }
}
```

Register:

```csharp
builder.Services.AddHostedService<EmailSenderService>();
```

### 6. Add global exception handling middleware

```csharp
// Middleware/ExceptionMiddleware.cs
public class ExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionMiddleware> _logger;

    public ExceptionMiddleware(RequestDelegate next, ILogger<ExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception for {Path}", context.Request.Path);
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { error = "An unexpected error occurred." });
        }
    }
}
```

Register before auth:

```csharp
app.UseMiddleware<ExceptionMiddleware>();
```

### 7. Add health checks and OpenAPI

```csharp
builder.Services.AddHealthChecks()
    .AddDbContextCheck<AppDbContext>();

// In pipeline
app.MapHealthChecks("/health");
```

### 8. EF Core query best practices

- Use `.AsNoTracking()` for read-only queries.
- Use `.Include()` / `.ThenInclude()` for eager loading only when needed.
- Project to DTOs with `.Select()` to avoid over-fetching.
- Always pass `CancellationToken` to async EF methods.
- Avoid `.ToList()` before filtering — push predicates to the database.

## Pitfalls

- **Never hardcode secrets in appsettings.json.** Use User Secrets locally, environment variables or Key Vault in production. Use `YOUR_KEY` placeholders in examples only.
- **Never call `SaveChangesAsync` without a `CancellationToken`** in endpoint or background service code.
- **Background services must use scoped services via `IServiceProvider.CreateScope()`.** Injecting a scoped `DbContext` directly into a singleton `BackgroundService` causes captive dependency bugs.
- **Do not use `DateTime.Now` for token expiry.** Always use `DateTime.UtcNow` to avoid timezone-related validation failures.
- **Do not over-fetch with `.Include()` on large graphs.** Prefer `.Select()` projection to DTOs.
- **Do not forget `app.UseAuthentication()` before `app.UseAuthorization()`** — order matters in the pipeline.
- **Do not run `dotnet ef database update` against a production database without a backup.** Migrations can be destructive.
- **Never delete migrations that have already been applied to any database.** If a migration is wrong, create a new corrective migration instead.
- **Assumes modern .NET (ASP.NET Core 8+).** Older .NET Framework projects require different patterns — confirm target framework before applying these steps.
- **Cloud-provider-specific deployment (Azure/AWS/GCP) is out of scope** unless explicitly requested.

## Verification

Run these checks after building or modifying the backend:

```powershell
# 1. Project builds cleanly
dotnet build

# 2. Run tests (if present)
dotnet test

# 3. EF Core migrations are valid
dotnet ef migrations list

# 4. Database schema is in sync
dotnet ef database update --dry-run

# 5. App starts and health check responds
dotnet run
# In another terminal:
curl http://localhost:5000/health
# Expected: "Healthy"

# 6. Swagger UI is reachable
# Navigate to http://localhost:5000/swagger
```

Expected build output:

```
Build succeeded.
    0 Warning(s)
    0 Error(s)
```

## Related Skills

- `ef-core-migrations` — deeper migration and schema management guidance
- `dotnet-testing` — xUnit, Moq, FluentAssertions, integration testing with `WebApplicationFactory`
- `dotnet-deployment` — containerization, CI/CD, and cloud deployment patterns
