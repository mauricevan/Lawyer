/** Scroll without animation when the user prefers reduced motion. */
export function scrollIntoViewRespectingMotion(
  element: HTMLElement | null | undefined,
  options: ScrollIntoViewOptions = { block: "nearest" },
): void {
  if (!element) return;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  element.scrollIntoView({
    ...options,
    behavior: reduceMotion ? "auto" : (options.behavior ?? "smooth"),
  });
}
