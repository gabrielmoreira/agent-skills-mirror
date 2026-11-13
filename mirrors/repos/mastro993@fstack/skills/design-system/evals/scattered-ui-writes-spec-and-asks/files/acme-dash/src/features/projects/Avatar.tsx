export function Avatar({ name, src, size = 32 }: { name: string; src?: string; size?: number }) {
  const initials = name.split(" ").map((p) => p[0]).join("").slice(0, 2).toUpperCase();
  return src ? (
    <img src={src} alt={name} width={size} height={size} className="rounded-full" />
  ) : (
    <span
      className="inline-flex items-center justify-center rounded-full bg-[#E8EEFF] text-xs font-semibold text-[#2F5BEA]"
      style={{ width: size, height: size }}
    >
      {initials}
    </span>
  );
}
