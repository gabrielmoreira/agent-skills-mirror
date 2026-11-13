import pg from "pg";

// Every team reads and writes every table through this pool.
export const db = new pg.Pool({ connectionString: process.env.DATABASE_URL });
