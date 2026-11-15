import express from "express";
import { requireUser } from "./auth.js";
import { notificationsRouter } from "./notifications/routes.js";
import { unsubscribeRouter } from "./notifications/unsubscribe.js";
import { usersRouter } from "./routes/users.js";

const app = express();
app.use(express.json());
app.use("/api/users", requireUser, usersRouter);
app.use("/api/notifications", requireUser, notificationsRouter);
app.use("/unsubscribe", express.urlencoded({ extended: false }), unsubscribeRouter);
app.use(express.static("web/public"));

const port = Number(process.env.PORT ?? 3000);
// Start the server
app.listen(port, () => console.log(`relay listening on ${port}`));
