import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Notification } from "@prisma/client";
import Handlebars from "handlebars";
import nunjucks from "nunjucks";
import { KIND_LABELS, isNotificationKind } from "../generated/notification-kinds.js";

const root = process.cwd();
const env = new nunjucks.Environment(new nunjucks.FileSystemLoader(join(root, "emails")), {
  autoescape: true,
  throwOnUndefined: true,
});

env.addFilter("shortDate", (iso: string) =>
  new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short" }),
);

const slackTemplates = new Map<string, HandlebarsTemplateDelegate>();

function slackTemplate(name: string): HandlebarsTemplateDelegate {
  let template = slackTemplates.get(name);
  if (!template) {
    template = Handlebars.compile(readFileSync(join(root, "templates/slack", `${name}.hbs`), "utf8"), {
      noEscape: true,
    });
    slackTemplates.set(name, template);
  }
  return template;
}

export type EmailContext = { name: string; unsubscribeUrl: string };

export function renderEmail(n: Notification, ctx: EmailContext): { subject: string; html: string; text: string } {
  const label = isNotificationKind(n.kind) ? KIND_LABELS[n.kind] : n.kind;
  const view = {
    ...ctx,
    label,
    title: n.title,
    body: n.body,
    data: n.data,
    items: (n.data as { items?: unknown[] }).items ?? [],
    appUrl: process.env.APP_URL ?? "https://relay.acme.dev",
  };
  const template = n.kind === "digest.weekly" ? "notification-digest.njk" : "notification.njk";
  const html = env.render(template, view);
  return { subject: n.title, html, text: `${n.title}\n\n${n.body}\n\nUnsubscribe: ${ctx.unsubscribeUrl}` };
}

export function renderSlack(n: Notification): string {
  return slackTemplate("mention")({
    title: n.title,
    body: n.body,
    kind: n.kind,
    actor: (n.data as { actor?: { name: string; url: string } }).actor,
    url: `${process.env.APP_URL ?? "https://relay.acme.dev"}/notifications/${n.id}`,
  });
}
