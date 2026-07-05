/** Title-case chip labels for clearer tap targets (Web Interface Guidelines). */
export function formatChoiceLabel(label: string): string {
  return label
    .split(/(\s+|\/+)/)
    .map((part) => {
      if (/^\s+$|^\/+$/.test(part) || part.length === 0) return part;
      return part.charAt(0).toLocaleUpperCase("nl-NL") + part.slice(1);
    })
    .join("");
}
