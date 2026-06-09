declare module 'fast-glob' {
  export default function fg(
    patterns: string[],
    options?: { cwd?: string; absolute?: boolean; onlyFiles?: boolean }
  ): Promise<string[]>
}

declare module '@duckdb/node-api' {
  export class DuckDBInstance {
    static create(path: string): Promise<DuckDBInstance>
    connect(): Promise<DuckDBConnection>
  }

  export class DuckDBConnection {
    run(sql: string): Promise<void>
    runAndReadAll(sql: string): Promise<{ getRowObjectsJson(): Record<string, unknown>[] }>
    createAppender(table: string): Promise<DuckDBAppender>
  }

  export class DuckDBAppender {
    appendNull(): void
    appendInteger(value: number): void
    appendVarchar(value: string): void
    endRow(): void
    close(): Promise<void>
    closeSync(): void
  }
}
