import { getLlmsIndex } from "@/lib/llm-content";

export const revalidate = false;

export function GET() {
  return new Response(getLlmsIndex().trimEnd() + "\n", {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}
