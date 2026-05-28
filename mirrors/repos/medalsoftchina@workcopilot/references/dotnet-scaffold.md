# .NET 8 WebAPI 脚手架模板

## 创建命令

```bash
dotnet new sln -n {ProjectName}
dotnet new webapi -n {ProjectName}.Api -o src/{ProjectName}.Api --use-controllers
dotnet new xunit -n {ProjectName}.Tests -o tests/{ProjectName}.Tests
dotnet sln add src/{ProjectName}.Api
dotnet sln add tests/{ProjectName}.Tests
dotnet add tests/{ProjectName}.Tests reference src/{ProjectName}.Api
```

## NuGet 核心包

```xml
<!-- src/{ProjectName}.Api/{ProjectName}.Api.csproj -->
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>

<ItemGroup>
  <!-- SqlSugar ORM（默认） -->
  <PackageReference Include="SqlSugarCore" Version="5.*" />
  <!-- SqlSugar 自动适配 SQL Server / PostgreSQL / MySQL / SQLite，无需额外 Provider -->

  <!-- 认证 -->
  <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.*" />
  <!-- 或 Azure AD: Microsoft.Identity.Web -->

  <!-- 日志 -->
  <PackageReference Include="Serilog.AspNetCore" Version="8.*" />

  <!-- Swagger -->
  <PackageReference Include="Swashbuckle.AspNetCore" Version="6.*" />

  <!-- 其他 -->
  <PackageReference Include="FluentValidation.AspNetCore" Version="11.*" />
  <PackageReference Include="AutoMapper" Version="13.*" />
</ItemGroup>

<!-- tests/{ProjectName}.Tests/{ProjectName}.Tests.csproj -->
<ItemGroup>
  <PackageReference Include="FluentAssertions" Version="6.*" />
  <PackageReference Include="Moq" Version="4.*" />
  <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.*" />
</ItemGroup>
```

## Program.cs 骨架

```csharp
using System.Reflection;
using Microsoft.OpenApi.Models;
using Serilog;
using {ProjectName}.Api.Infrastructure.Database;
using {ProjectName}.Api.Infrastructure.Auth;
using {ProjectName}.Api.Infrastructure.Middleware;
using {ProjectName}.Api.Infrastructure.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Serilog
builder.Host.UseSerilog((ctx, cfg) => cfg.ReadFrom.Configuration(ctx.Configuration));

// SqlSugar ORM
builder.Services.AddSqlSugarSetup(builder.Configuration);

// Authentication
builder.Services.AddJwtAuthentication(builder.Configuration);

// Services & Repositories
builder.Services.AddApplicationServices();

// Controllers
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// Swagger（含 JWT 认证头，支持在线调试）
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "{ProjectName} API",
        Version = "v1",
        Description = "{项目描述}"
    });
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "输入 JWT Token（不含 Bearer 前缀）"
    });
    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
    // 加载 XML 注释
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath)) options.IncludeXmlComments(xmlPath);
});

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy.WithOrigins(builder.Configuration.GetSection("AllowedOrigins").Get<string[]>() ?? [])
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials());
});

// FluentValidation
builder.Services.AddFluentValidationAutoValidation();

var app = builder.Build();

// Middleware pipeline
app.UseGlobalExceptionHandler();
app.UseSerilogRequestLogging();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "{ProjectName} API v1");
        c.DocExpansion(Swashbuckle.AspNetCore.SwaggerUI.DocExpansion.None);
    });
    // Code First 自动建表（仅开发环境）
    app.InitDatabase();
}

app.UseCors();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

## 关键文件模板

### Infrastructure/Auth/JwtAuthExtensions.cs

```csharp
public static class JwtAuthExtensions
{
    public static IServiceCollection AddJwtAuthentication(
        this IServiceCollection services, IConfiguration configuration)
    {
        var jwtSettings = configuration.GetSection("Jwt");
        services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new TokenValidationParameters
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateLifetime = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = jwtSettings["Issuer"],
                    ValidAudience = jwtSettings["Audience"],
                    IssuerSigningKey = new SymmetricSecurityKey(
                        Encoding.UTF8.GetBytes(jwtSettings["Secret"]!))
                };
            });
        return services;
    }
}
```

### Infrastructure/Middleware/GlobalExceptionMiddleware.cs

```csharp
public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger)
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
            _logger.LogError(ex, "Unhandled exception");
            // 生产环境不暴露内部异常细节
            var (statusCode, message) = ex switch
            {
                ArgumentException => (400, ex.Message),
                UnauthorizedAccessException => (401, "未授权访问"),
                KeyNotFoundException => (404, "资源不存在"),
                _ => (500, "服务器内部错误，请联系管理员")
            };
            context.Response.StatusCode = statusCode;
            await context.Response.WriteAsJsonAsync(new
            {
                error = message,
                traceId = context.TraceIdentifier
            });
        }
    }
}

public static class GlobalExceptionMiddlewareExtensions
{
    public static IApplicationBuilder UseGlobalExceptionHandler(this IApplicationBuilder app)
        => app.UseMiddleware<GlobalExceptionMiddleware>();
}
```

### Infrastructure/Database/SqlSugarSetup.cs

```csharp
using SqlSugar;

public static class SqlSugarSetup
{
    public static void AddSqlSugarSetup(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("Default");
        // 根据数据库类型选择 DbType：SqlServer / PostgreSQL / MySql / Sqlite
        var dbType = configuration.GetValue<string>("Database:DbType") ?? "SqlServer";

        services.AddSingleton<ISqlSugarClient>(sp =>
        {
            var db = new SqlSugarScope(new ConnectionConfig
            {
                ConnectionString = connectionString,
                DbType = Enum.Parse<DbType>(dbType),
                IsAutoCloseConnection = true,
                InitKeyType = InitKeyType.Attribute
            },
            db =>
            {
                // 全局 SQL 日志（仅开发环境）
                var env = sp.GetRequiredService<IWebHostEnvironment>();
                if (env.IsDevelopment())
                {
                    db.Aop.OnLogExecuting = (sql, pars) =>
                    {
                        var logger = sp.GetRequiredService<ILogger<SqlSugarScope>>();
                        logger.LogDebug("SQL: {Sql}", sql);
                    };
                }
            });
            return db;
        });
    }

    /// <summary>
    /// Code First 初始化数据库表结构
    /// </summary>
    public static void InitDatabase(this IApplicationBuilder app)
    {
        var db = app.ApplicationServices.GetRequiredService<ISqlSugarClient>();
        // 自动建表（如已存在则跳过）
        db.DbMaintenance.CreateDatabase();
        db.CodeFirst.InitTables(
            typeof(User)
            // 新增 Entity 在此追加
        );
    }
}
```

### Models/Entities/User.cs

```csharp
using SqlSugar;

[SugarTable("Users")]
public class User
{
    [SugarColumn(IsPrimaryKey = true)]
    public Guid Id { get; set; } = Guid.NewGuid();

    [SugarColumn(Length = 50, IsNullable = false, UniqueGroupNameList = new[] { "UK_Username" })]
    public string Username { get; set; } = string.Empty;

    [SugarColumn(Length = 255, IsNullable = false)]
    public string Email { get; set; } = string.Empty;

    [SugarColumn(Length = 255, IsNullable = false)]
    public string PasswordHash { get; set; } = string.Empty;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    [SugarColumn(IsNullable = true)]
    public DateTime? UpdatedAt { get; set; }

    public bool IsActive { get; set; } = true;
}
```

### Controllers/HealthController.cs

```csharp
[ApiController]
[Route("api/[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    public IActionResult Get() => Ok(new { status = "healthy", timestamp = DateTime.UtcNow });
}
```

### appsettings.json 结构

```json
{
  "ConnectionStrings": {
    "Default": "Server=localhost;Database={ProjectName};Trusted_Connection=true;TrustServerCertificate=true;"
  },
  "Database": {
    "DbType": "SqlServer"
  },
  "Jwt": {
    "Issuer": "{ProjectName}",
    "Audience": "{ProjectName}",
    "Secret": "CHANGE-THIS-USE-dotnet-user-secrets-IN-PRODUCTION",
    "ExpiryMinutes": 60
  },
  "AllowedOrigins": ["http://localhost:5173"],
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "SqlSugar": "Warning"
      }
    },
    "WriteTo": [
      { "Name": "Console" },
      { "Name": "File", "Args": { "path": "logs/log-.txt", "rollingInterval": "Day" } }
    ]
  }
}
```

### Dockerfile（多阶段构建）

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["{ProjectName}.sln", "."]
COPY ["src/{ProjectName}.Api/{ProjectName}.Api.csproj", "src/{ProjectName}.Api/"]
RUN dotnet restore
COPY . .
RUN dotnet publish src/{ProjectName}.Api -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENTRYPOINT ["dotnet", "{ProjectName}.Api.dll"]
```

### .dockerignore

```
**/.git
**/.vs
**/bin
**/obj
**/.gitignore
**/logs
**/*.user
**/*.suo
README.md
COPILOT_README.md
.github/
rules/
tests/
```

### docker-compose.yml（项目根目录）

```yaml
services:
  backend:
    build:
      context: ./{project-name}
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__Default=Server=db;Database={ProjectName};User=sa;Password=${DB_PASSWORD:-YourStrong!Pass123};TrustServerCertificate=true
      - Jwt__Secret=${JWT_SECRET:-dev-only-secret-change-in-production-32chars}
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./{project-name}-web
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - MSSQL_SA_PASSWORD=${DB_PASSWORD:-YourStrong!Pass123}
    ports:
      - "1433:1433"
    volumes:
      - db-data:/var/opt/mssql
    healthcheck:
      test: /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" || exit 1
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  db-data:
```

### .env.docker（Docker Compose 环境变量模板）

```env
# 数据库
DB_PASSWORD=YourStrong!Pass123

# JWT
JWT_SECRET=change-this-to-a-secure-secret-at-least-32-chars

# 前端 API 地址（如需覆盖）
# VITE_API_BASE_URL=/api
```

> **使用方式**：复制为 `.env` 并修改密码，然后 `docker compose up -d`

### Infrastructure/Extensions/ServiceCollectionExtensions.cs

```csharp
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(this IServiceCollection services)
    {
        // 注册业务服务（按需添加）
        // services.AddScoped<IUserService, UserService>();
        // services.AddScoped<IUserRepository, UserRepository>();

        // AutoMapper
        services.AddAutoMapper(typeof(ServiceCollectionExtensions).Assembly);

        return services;
    }
}
```

### .editorconfig

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{csproj,json,yml,yaml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### Directory.Build.props

```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

### .gitignore

```
bin/
obj/
.vs/
*.user
*.suo
appsettings.*.local.json
logs/
*.log
```

> **安全提醒**：
> - 生产环境的 JWT Secret 必须使用 `dotnet user-secrets` 或环境变量注入，**严禁**提交到代码仓库
> - `appsettings.json` 中的 Secret 仅用于本地开发
> - 连接字符串同理，生产使用 Azure Key Vault 或环境变量
