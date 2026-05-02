"use client";

import { useEffect, useState } from "react";
import { copy, type Lang } from "@/lib/copy";

const STORAGE = "four_persimmons_lang";

function pickLang(nav?: string): Lang {
  const n = (nav ?? "").toLowerCase();
  return n.startsWith("en") ? "en" : "zh";
}

export default function Home() {
  const [lang, setLang] = useState<Lang>("zh");

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE) as Lang | null;
    setLang(saved === "en" || saved === "zh" ? saved : pickLang(navigator.language));
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE, lang);
    document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
  }, [lang]);

  const c = copy[lang];

  return (
    <>
      {/* Fixed header — padded for iOS safe area */}
      <header className="fixed inset-x-0 top-0 z-40 border-b border-persimmon-200/80 bg-persimmon-50/90 backdrop-blur-md supports-[backdrop-filter]:bg-persimmon-50/70 pt-[calc(0.5rem+var(--safe-top))]">
        <div className="mx-auto flex max-w-3xl items-center justify-between gap-3 px-4 pb-3">
          <div className="min-w-0">
            <p className="font-serif text-[clamp(1.125rem,4.5vw,1.375rem)] font-bold leading-tight text-persimmon-800 truncate">
              {c.navBrandFull}
            </p>
            <p className="text-[11px] tracking-[0.18em] text-persimmon-600">
              BAKEY · BRAND DEMO
            </p>
          </div>
          <div
            className="flex shrink-0 items-center gap-0.5 rounded-full border border-persimmon-200 bg-white/75 p-0.5 shadow-sm"
            role="group"
            aria-label={c.langAria}
          >
            <button
              type="button"
              onClick={() => setLang("zh")}
              aria-pressed={lang === "zh"}
              className={`tap-target flex items-center justify-center rounded-full px-3 text-xs font-semibold tracking-wide transition ${
                lang === "zh"
                  ? "bg-persimmon-600 text-white"
                  : "text-persimmon-600 hover:bg-persimmon-100"
              }`}
            >
              {c.langZh}
            </button>
            <button
              type="button"
              onClick={() => setLang("en")}
              aria-pressed={lang === "en"}
              className={`tap-target flex items-center justify-center rounded-full px-3 text-[11px] font-semibold tracking-wide transition ${
                lang === "en"
                  ? "bg-persimmon-600 text-white"
                  : "text-persimmon-600 hover:bg-persimmon-100"
              }`}
            >
              {c.langEn}
            </button>
          </div>
        </div>
      </header>

      <main className="relative mx-auto flex max-w-3xl flex-col gap-[clamp(2.75rem,8vw,4.5rem)] px-4 pb-[calc(2.5rem+var(--safe-bottom))] pt-[calc(7rem+var(--safe-top))]">
        {/* Hero */}
        <section aria-labelledby="hero-title" className="text-center" id="hero">
          <div className="relative isolate overflow-hidden rounded-2xl border border-persimmon-200/90 bg-gradient-to-br from-white via-persimmon-50 to-persimmon-200/60 px-5 py-[clamp(2.75rem,9vw,4.25rem)] shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
            <div
              className="pointer-events-none absolute -right-24 -top-28 h-[14rem] w-[14rem] rounded-full bg-persimmon-300/30 blur-3xl"
              aria-hidden
            />
            <div
              className="pointer-events-none absolute -bottom-32 -left-16 h-[12rem] w-[12rem] rounded-full bg-amber-200/35 blur-3xl"
              aria-hidden
            />
            <p className="text-[11px] font-semibold uppercase tracking-[0.35em] text-persimmon-600">
              {c.heroKicker}
            </p>
            <h1
              id="hero-title"
              className="font-serif mt-3 text-[clamp(2rem,11vw,3.125rem)] font-bold leading-[1.12] tracking-tight text-persimmon-900"
            >
              {c.heroTitle}
            </h1>
            <p className="mx-auto mt-5 max-w-md text-[clamp(0.95rem,3.9vw,1.05rem)] leading-relaxed text-persimmon-800/92">
              {c.heroSubline}
            </p>
            <a
              href="#about"
              className="tap-target mx-auto mt-8 inline-flex items-center justify-center rounded-full bg-persimmon-700 px-6 py-2.5 text-sm font-semibold text-white shadow-md shadow-persimmon-900/18 transition hover:bg-persimmon-600 active:scale-[0.98]"
            >
              {c.heroScroll}
            </a>
          </div>
        </section>

        {/* About */}
        <section id="about" aria-labelledby="about-h" className="scroll-mt-36">
          <h2 id="about-h" className="font-serif text-2xl font-bold text-persimmon-800">
            {c.aboutTitle}
          </h2>
          <p className="mt-4 text-[clamp(1rem,3.9vw,1.0625rem)] leading-relaxed text-persimmon-800/92">
            {c.aboutBody}
          </p>
        </section>

        {/* Pillars */}
        <section aria-labelledby="craft-h" className="scroll-mt-36">
          <h2 id="craft-h" className="font-serif text-2xl font-bold text-persimmon-800">
            {c.craftTitle}
          </h2>
          <ul className="mt-5 flex flex-col gap-3">
            {[c.craft1, c.craft2, c.craft3].map((line) => (
              <li
                key={line}
                className="rounded-xl border border-persimmon-200/95 bg-white/70 px-[1.0625rem] py-3 text-[clamp(1rem,3.85vw,1.05rem)] leading-snug shadow-sm backdrop-blur-sm"
              >
                <span className="mr-2 inline-flex h-[1em] align-[-2px]" aria-hidden>
                  ●
                </span>
                {line}
              </li>
            ))}
          </ul>
        </section>

        {/* Hours */}
        <section aria-labelledby="hours-h" className="scroll-mt-36">
          <h2 id="hours-h" className="font-serif text-2xl font-bold text-persimmon-800">
            {c.hoursTitle}
          </h2>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl border border-persimmon-200 bg-white/75 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-persimmon-600">
                {c.weekdays}
              </p>
              <p className="font-serif mt-1 text-xl font-semibold text-persimmon-900">
                07:30 – 18:30
              </p>
            </div>
            <div className="rounded-xl border border-persimmon-200 bg-white/75 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-persimmon-600">
                {c.weekend}
              </p>
              <p className="font-serif mt-1 text-xl font-semibold text-persimmon-900">
                08:30 – 19:30
              </p>
            </div>
          </div>
          <div className="mt-4 rounded-xl border border-dashed border-persimmon-300/90 bg-persimmon-100/40 px-4 py-3 text-sm text-persimmon-700">
            <p className="font-medium">{c.closed}</p>
            <p className="mt-1 text-[13px] text-persimmon-700/85">{c.hoursNote}</p>
          </div>
        </section>

        {/* Gallery placeholders */}
        <section aria-labelledby="gal-h" className="scroll-mt-36">
          <h2 id="gal-h" className="font-serif text-2xl font-bold text-persimmon-800">
            {c.galleryTitle}
          </h2>
          <p className="mt-2 text-sm leading-relaxed text-persimmon-700">{c.galleryCaption}</p>
          <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {[
              "from-persimmon-400/90 to-persimmon-200/85",
              "from-amber-700/95 to-orange-800/98",
              "from-orange-950/93 to-orange-950/93",
              "from-orange-950/93 to-orange-950/93",
              "from-amber-200/95 to-orange-950/93",
              "from-persimmon-500/93 to-orange-950/93",
            ].map((fromTo, i) => (
              <div
                key={i}
                className={`relative aspect-square overflow-hidden rounded-xl bg-gradient-to-br ${fromTo} shadow-inner`}
              >
                <span className="sr-only">{c.galleryCaption}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Contact */}
        <section aria-labelledby="con-h" className="scroll-mt-36 pb-6">
          <h2 id="con-h" className="font-serif text-2xl font-bold text-persimmon-800">
            {c.contactTitle}
          </h2>
          <div className="mt-4 space-y-3 rounded-xl border border-persimmon-200 bg-white/85 p-5 text-[clamp(0.95rem,3.8vw,1.05rem)] leading-relaxed text-persimmon-900">
            <p>{c.addressLine}</p>
            <p className="text-persimmon-800/92">{c.wechatPlaceholder}</p>
            <p className="text-persimmon-800/92">{c.phonePlaceholder}</p>
          </div>
        </section>

        <footer className="border-t border-persimmon-200/90 pt-6 text-center">
          <a
            href="/home.html"
            className="tap-target mx-auto mb-6 inline-flex min-w-[160px] items-center justify-center rounded-full border border-persimmon-300 bg-white/85 px-5 text-xs font-semibold uppercase tracking-[0.16em] text-persimmon-700 hover:border-persimmon-500 hover:bg-persimmon-50 active:scale-[0.98]"
            aria-label={c.backHomeAria}
          >
            ← {c.backHomeLabel}
          </a>
          <p className="text-[11px] leading-relaxed tracking-wide text-persimmon-600">
            © {new Date().getFullYear()} {c.navBrandFull}
            <br aria-hidden />
            <span>{c.footerTiny}</span>
            www.lava7397.com
          </p>
        </footer>
      </main>
    </>
  );
}
