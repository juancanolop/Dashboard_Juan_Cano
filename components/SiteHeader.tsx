"use client";

import { useEffect, useState } from "react";
import Logo from "./Logo";

// Same nav as the main site, but pointing at absolute URLs since this app
// lives on a different subdomain (dashboard.juandavidcano.com).
const SITE_URL = "https://www.juandavidcano.com";
const NAV_LINKS = [
  { label: "Projects", href: `${SITE_URL}/#case-study`, newTab: false },
  { label: "About Me", href: `${SITE_URL}/about-me`, newTab: false },
  { label: "Blog", href: "https://news.kronosgmt.com/", newTab: true },
];
const CALENDLY = "https://calendly.com/juancano-kronosgmt/introduction-meeting?primary_color=5f7ba3";

/** Same header as juandavidcano.com (dodecahedron logo + nav), so the
 *  dashboard reads as part of the same site instead of a separate app. */
export default function SiteHeader() {
  const [open, setOpen] = useState(false);

  // Leaflet's zoom controls/attribution render in their own GPU-composited
  // layer that ignores this overlay's z-index in some browsers, so hide
  // them outright while the mobile menu is open rather than fight it.
  useEffect(() => {
    document.body.classList.toggle("mobile-menu-open", open);
    return () => document.body.classList.remove("mobile-menu-open");
  }, [open]);

  return (
    <>
      <header className="site-header sticky top-0 z-50 border-b border-white/10 bg-bg">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-8 px-5 py-4">
          <Logo href={SITE_URL + "/"} />

          <nav className="hidden items-center gap-8 md:flex">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.newTab ? "_blank" : undefined}
                rel={link.newTab ? "noreferrer" : undefined}
                className="text-sm text-white/80 transition hover:text-white"
              >
                {link.label}
              </a>
            ))}
            <a
              href={CALENDLY}
              target="_blank"
              rel="noreferrer"
              className="glow-pill rounded-full px-5 py-2 text-sm text-white transition hover:bg-white/10"
            >
              Get in Touch
            </a>
          </nav>

          <button
            onClick={() => setOpen(true)}
            aria-label="Open menu"
            className="flex h-9 w-9 items-center justify-center rounded-md border border-white/20 md:hidden"
          >
            <span className="sr-only">Menu</span>
            <div className="space-y-1.5">
              <span className="block h-0.5 w-5 bg-white" />
              <span className="block h-0.5 w-5 bg-white" />
              <span className="block h-0.5 w-5 bg-white" />
            </div>
          </button>
        </div>
      </header>

      {/* Rendered as a sibling of <header>, not a descendant — nesting a
          position:fixed overlay inside a position:sticky ancestor caused a
          compositing bug in some browsers where hit-testing/geometry were
          correct (full-viewport) but the painted layer wasn't, letting page
          content show through. */}
      {open && (
        <div
          className="fixed inset-0 z-[999] flex flex-col bg-bg md:hidden"
          style={{ transform: "translateZ(0)", willChange: "transform" }}
        >
          <div className="flex items-center justify-between px-5 py-4">
            <Logo href={SITE_URL + "/"} />
            <button
              onClick={() => setOpen(false)}
              aria-label="Close menu"
              className="flex h-9 w-9 items-center justify-center rounded-md border border-white/20 text-2xl leading-none text-white"
            >
              ×
            </button>
          </div>

          <nav className="flex flex-1 flex-col items-center justify-center gap-8">
            {NAV_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target={link.newTab ? "_blank" : undefined}
                rel={link.newTab ? "noreferrer" : undefined}
                onClick={() => setOpen(false)}
                className="text-2xl text-white transition hover:text-white/70"
              >
                {link.label}
              </a>
            ))}
            <a
              href={CALENDLY}
              target="_blank"
              rel="noreferrer"
              onClick={() => setOpen(false)}
              className="glow-pill mt-2 rounded-full px-6 py-3 text-base text-white transition hover:bg-white/10"
            >
              Get in Touch
            </a>
          </nav>
        </div>
      )}
    </>
  );
}
