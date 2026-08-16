"use client";

import { useLayoutEffect, useState } from "react";

/** True below the given breakpoint (matches Tailwind's `lg` = 1024px by
 *  default). Starts `false` (desktop) so server-rendered HTML and the first
 *  client render match; a `useLayoutEffect` (runs before paint) flips it
 *  before the user sees anything, so there's no visible flash on mobile. */
export function useIsMobile(breakpointPx = 1024): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useLayoutEffect(() => {
    const mql = window.matchMedia(`(max-width: ${breakpointPx - 1}px)`);
    const update = () => setIsMobile(window.innerWidth < breakpointPx);
    update();
    // Some viewport-emulation tools resize without firing the MediaQueryList
    // "change" event, so also listen for plain window resizes as a fallback.
    mql.addEventListener("change", update);
    window.addEventListener("resize", update);
    return () => {
      mql.removeEventListener("change", update);
      window.removeEventListener("resize", update);
    };
  }, [breakpointPx]);

  return isMobile;
}
