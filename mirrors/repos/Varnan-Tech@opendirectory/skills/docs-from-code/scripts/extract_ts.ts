/**
 * docs-from-code — TypeScript/JavaScript Code Extractor
 * Uses ts-morph to extract structured metadata from a TS/JS codebase.
 * Outputs a JSON file the agent feeds to Gemini for doc generation.
 *
 * Usage: npx ts-node extract_ts.ts <project-root> [output-file]
 */

import { Project, SyntaxKind, SourceFile } from "ts-morph";
import * as fs from "fs";
import * as path from "path";

interface FunctionDoc {
  name: string;
  signature: string;
  description: string;
  params: { name: string; type: string; description: string }[];
  returns: string;
  file: string;
  isExported: boolean;
}

interface RouteDoc {
  method: string;
  path: string;
  handler: string;
  description: string;
  file: string;
}

interface TypeDoc {
  name: string;
  kind: "interface" | "type" | "enum" | "class";
  definition: string;
  description: string;
  file: string;
}

interface CodeMetadata {
  projectName: string;
  language: "typescript" | "javascript";
  framework: string | null;
  entryPoints: string[];
  functions: FunctionDoc[];
  routes: RouteDoc[];
  types: TypeDoc[];
  dependencies: Record<string, string>;
  scripts: Record<string, string>;
}

function detectFramework(pkgJson: any): string | null {
  const deps = {
    ...pkgJson.dependencies,
    ...pkgJson.devDependencies,
  };
  if (deps["next"]) return "nextjs";
  if (deps["express"]) return "express";
  if (deps["hono"]) return "hono";
  if (deps["fastify"]) return "fastify";
  if (deps["@nestjs/core"]) return "nestjs";
  if (deps["koa"]) return "koa";
  if (deps["@sveltejs/kit"]) return "sveltekit";
  if (deps["astro"]) return "astro";
  return null;
}

function extractJsDocComment(node: any): string {
  try {
    const docs = node.getJsDocs?.();
    if (docs && docs.length > 0) {
      return docs[0].getDescription().trim();
    }
  } catch {}
  return "";
}

function extractRoutes(sourceFile: SourceFile, framework: string | null): RouteDoc[] {
  const routes: RouteDoc[] = [];
  const filePath = sourceFile.getFilePath();

  // Express / Hono / Fastify / Koa style: app.get('/path', handler)
  const callExpressions = sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression);
  for (const call of callExpressions) {
    const expr = call.getExpression().getText();
    const httpMethods = ["get", "post", "put", "patch", "delete", "options", "head"];
    const methodMatch = httpMethods.find((m) => expr.endsWith(`.${m}`));
    if (methodMatch) {
      const args = call.getArguments();
      if (args.length >= 1) {
        const routePath = args[0].getText().replace(/['"]/g, "");
        routes.push({
          method: methodMatch.toUpperCase(),
          path: routePath,
          handler: args[1]?.getText()?.slice(0, 80) || "",
          description: "",
          file: filePath,
        });
      }
    }
  }

  // Next.js app router: export async function GET/POST etc
  if (framework === "nextjs" && filePath.includes("/api/")) {
    const functions = sourceFile.getFunctions();
    for (const fn of functions) {
      const name = fn.getName() || "";
      const httpMethods = ["GET", "POST", "PUT", "PATCH", "DELETE"];
      if (httpMethods.includes(name) && fn.isExported()) {
        const routePath = filePath
          .replace(/.*\/app/, "")
          .replace(/\/route\.(ts|tsx|js|jsx)$/, "")
          || "/";
        routes.push({
          method: name,
          path: routePath,
          handler: fn.getName() || "",
          description: extractJsDocComment(fn),
          file: filePath,
        });
      }
    }
  }

  return routes;
}

function extractFunctions(sourceFile: SourceFile): FunctionDoc[] {
  const functions: FunctionDoc[] = [];
  const filePath = sourceFile.getFilePath();

  // Regular functions
  for (const fn of sourceFile.getFunctions()) {
    if (!fn.isExported()) continue;
    const name = fn.getName() || "anonymous";
    const params = fn.getParameters().map((p) => ({
      name: p.getName(),
      type: p.getType().getText(),
      description: "",
    }));
    functions.push({
      name,
      signature: `${name}(${fn.getParameters().map((p) => p.getText()).join(", ")}): ${fn.getReturnType().getText()}`,
      description: extractJsDocComment(fn),
      params,
      returns: fn.getReturnType().getText(),
      file: filePath,
      isExported: true,
    });
  }

  // Arrow functions assigned to exported const
  for (const varDecl of sourceFile.getVariableDeclarations()) {
    const init = varDecl.getInitializer();
    if (!init) continue;
    const isArrow = init.getKind() === SyntaxKind.ArrowFunction;
    if (!isArrow) continue;
    const varStatement = varDecl.getVariableStatement();
    if (!varStatement?.isExported()) continue;
    const name = varDecl.getName();
    functions.push({
      name,
      signature: `${name} = ${init.getText().slice(0, 120)}`,
      description: extractJsDocComment(varStatement),
      params: [],
      returns: "",
      file: filePath,
      isExported: true,
    });
  }

  return functions;
}

function extractTypes(sourceFile: SourceFile): TypeDoc[] {
  const types: TypeDoc[] = [];
  const filePath = sourceFile.getFilePath();

  for (const iface of sourceFile.getInterfaces()) {
    if (!iface.isExported()) continue;
    types.push({
      name: iface.getName(),
      kind: "interface",
      definition: iface.getText().slice(0, 400),
      description: extractJsDocComment(iface),
      file: filePath,
    });
  }

  for (const typeAlias of sourceFile.getTypeAliases()) {
    if (!typeAlias.isExported()) continue;
    types.push({
      name: typeAlias.getName(),
      kind: "type",
      definition: typeAlias.getText().slice(0, 400),
      description: extractJsDocComment(typeAlias),
      file: filePath,
    });
  }

  for (const cls of sourceFile.getClasses()) {
    if (!cls.isExported()) continue;
    types.push({
      name: cls.getName() || "AnonymousClass",
      kind: "class",
      definition: cls.getText().slice(0, 600),
      description: extractJsDocComment(cls),
      file: filePath,
    });
  }

  return types;
}

async function main() {
  const projectRoot = process.argv[2] || process.cwd();
  const outputFile = process.argv[3] || path.join(projectRoot, ".docs-extract.json");

  // Load package.json
  const pkgPath = path.join(projectRoot, "package.json");
  let pkgJson: any = {};
  if (fs.existsSync(pkgPath)) {
    pkgJson = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));
  }

  const framework = detectFramework(pkgJson);

  // Init ts-morph project
  const project = new Project({
    tsConfigFilePath: fs.existsSync(path.join(projectRoot, "tsconfig.json"))
      ? path.join(projectRoot, "tsconfig.json")
      : undefined,
    addFilesFromTsConfig: false,
  });

  // Add source files — skip node_modules, .next, dist, build
  const extensions = [".ts", ".tsx"];
  const skipDirs = ["node_modules", ".next", "dist", "build", ".turbo", "coverage", ".cache"];

  function addFiles(dir: string) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory()) {
        if (!skipDirs.includes(entry.name)) {
          addFiles(path.join(dir, entry.name));
        }
      } else if (extensions.some((ext) => entry.name.endsWith(ext))) {
        project.addSourceFileAtPath(path.join(dir, entry.name));
      }
    }
  }

  addFiles(projectRoot);

  const metadata: CodeMetadata = {
    projectName: pkgJson.name || path.basename(projectRoot),
    language: "typescript",
    framework,
    entryPoints: [],
    functions: [],
    routes: [],
    types: [],
    dependencies: pkgJson.dependencies || {},
    scripts: pkgJson.scripts || {},
  };

  for (const sourceFile of project.getSourceFiles()) {
    metadata.functions.push(...extractFunctions(sourceFile));
    metadata.routes.push(...extractRoutes(sourceFile, framework));
    metadata.types.push(...extractTypes(sourceFile));
  }

  // Detect entry points
  const commonEntries = ["src/index.ts", "index.ts", "src/main.ts", "server.ts", "app.ts"];
  metadata.entryPoints = commonEntries
    .filter((e) => fs.existsSync(path.join(projectRoot, e)))
    .map((e) => e);

  fs.writeFileSync(outputFile, JSON.stringify(metadata, null, 2));

  console.log(`Extracted ${metadata.functions.length} functions, ${metadata.routes.length} routes, ${metadata.types.length} types`);
  console.log(`Output: ${outputFile}`);
}

main().catch(console.error);
