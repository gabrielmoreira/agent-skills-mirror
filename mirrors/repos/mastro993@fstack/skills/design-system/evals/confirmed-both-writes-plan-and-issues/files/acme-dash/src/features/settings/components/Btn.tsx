import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "solid" | "outline" | "danger";
  small?: boolean;
};

export default function Btn({ variant = "solid", small, ...rest }: Props) {
  const colors = {
    solid: "bg-[#2F5BEA] text-white hover:bg-[#2549c4]",
    outline: "border border-[#E3E5EA] text-[#16181D]",
    danger: "bg-[#C8372D] text-white",
  }[variant];
  return (
    <button
      className={`${colors} ${small ? "px-3 py-1 text-xs" : "px-[18px] py-[9px] text-sm"} font-medium`}
      style={{ borderRadius: 6 }}
      {...rest}
    />
  );
}
