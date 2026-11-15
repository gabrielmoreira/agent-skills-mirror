import express from "express";
import { requireUser } from "./auth.js";
import { usersRouter } from "./routes/users.js";

const app = express();
app.use(express.json());
app.use("/api/users", requireUser, usersRouter);

const port = Number(process.env.PORT ?? 3000);
// Start the server
app.listen(port, () => console.log(`relay listening on ${port}`));
