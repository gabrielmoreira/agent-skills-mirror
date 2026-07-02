function normalize(parts: string[]): string {
  if (parts.length === 0) return "";
  const result: string[] = [];
  for (let index = 0; index < parts.length; index += 1) {
    let part = parts[index];
    if (typeof part !== "string") {
      throw new TypeError(`Url must be a string. Received ${part}`);
    }
    if (part === "") continue;
    if (index > 0) part = part.replace(/^[\/]+/, "");
    if (index < parts.length - 1) {
      part = part.replace(/[\/]+$/, "");
    } else {
      part = part.replace(/[\/]+$/, "/");
    }
    result.push(part);
  }
  return result.join("/").replace(/\/(\?|&|#[^!])/g, "$1");
}

export default function urlJoin(...parts: string[]): string {
  return normalize(parts);
}
