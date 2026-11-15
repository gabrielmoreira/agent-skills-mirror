import { SESv2Client, SendEmailCommand } from "@aws-sdk/client-sesv2";
import type { Notification } from "@prisma/client";
import { db } from "../../db.js";
import { renderEmail } from "../templates.js";
import type { DeliveryResult } from "../types.js";
import { unsubscribeUrl } from "../unsubscribe.js";

const ses = new SESv2Client({});
const FROM = process.env.NOTIFY_FROM ?? "Relay <notify@relay.acme.dev>";
const RETRYABLE = new Set(["TooManyRequestsException", "InternalFailure", "ServiceUnavailable", "LimitExceededException"]);

export async function sendEmail(n: Notification): Promise<DeliveryResult> {
  const user = await db.user.findUniqueOrThrow({ where: { id: n.userId } });
  const unsubscribe = unsubscribeUrl(user.id, "EMAIL");
  const { subject, html, text } = renderEmail(n, {
    name: user.name ?? user.email,
    unsubscribeUrl: unsubscribe,
  });

  try {
    // Send the email
    const out = await ses.send(
      new SendEmailCommand({
        FromEmailAddress: FROM,
        Destination: { ToAddresses: [user.email] },
        Content: {
          Simple: {
            Subject: { Data: subject },
            Body: { Html: { Data: html }, Text: { Data: text } },
            Headers: [
              { Name: "List-Unsubscribe", Value: `<${unsubscribe}>` },
              { Name: "List-Unsubscribe-Post", Value: "List-Unsubscribe=One-Click" },
            ],
          },
        },
      }),
    );
    return { ok: true, providerId: out.MessageId ?? "" };
  } catch (err) {
    const name = err instanceof Error ? err.name : "Unknown";
    return { ok: false, retryable: RETRYABLE.has(name), error: `${name}: ${String(err)}` };
  }
}
