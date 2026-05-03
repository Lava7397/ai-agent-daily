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

  const spots = [
    {
      title: c.spot1Title,
      body: c.spot1Body,
      link: c.spot1Cta,
      gradient: "from-orange-950 via-neutral-950 to-black",
      hash: "#about",
    },
    {
      title: c.spot2Title,
      body: c.spot2Body,
      link: c.spot2Cta,
      gradient: "from-amber-950/90 via-stone-950 to-neutral-950",
      hash: "#gallery",
    },
    {
      title: c.spot3Title,
      body: c.spot3Body,
      link: c.spot3Cta,
      gradient: "from-persimmon-900 via-neutral-900 to-black",
      hash: "#contact",
    },
  ] as const;

  return (
    <>
      {/* Retail-style global nav */}
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-ink/95 text-white backdrop-blur-md supports-[backdrop-filter]:bg-ink/85">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-3 pt-[calc(0.75rem+var(--safe-top))] md:px-8">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <span className="font-display truncate text-lg font-bold uppercase tracking-tighter md:text-xl">
              {c.navBrandShort}
            </span>
            <span className="hidden text-white/40 md:inline">/</span>
            <span className="hidden truncate font-display text-sm font-medium text-white/75 sm:inline">
              {c.navBrandFull}
            </span>
          </div>

          <nav
            className="hidden items-center gap-7 text-[13px] font-medium uppercase tracking-[0.14em] text-white/80 lg:flex"
            aria-label="sections"
          >
            <a href="#spotlight" className="transition hover:text-white">
              {c.navAnchorSpotlight}
            </a>
            <a href="#about" className="transition hover:text-white">
              {c.navAnchorStory}
            </a>
            <a href="#contact" className="transition hover:text-white">
              {c.navAnchorVisit}
            </a>
          </nav>

          <div
            className="flex shrink-0 items-center gap-2 border border-white/20 bg-white/[0.06] p-1"
            role="group"
            aria-label={c.langAria}
          >
            <button
              type="button"
              onClick={() => setLang("zh")}
              aria-pressed={lang === "zh"}
              className={`tap-target flex min-w-[44px] items-center justify-center px-3 text-[11px] font-bold uppercase tracking-[0.12em] transition ${
                lang === "zh" ? "bg-white text-black" : "text-white/70 hover:text-white"
              }`}
            >
              {c.langZh}
            </button>
            <button
              type="button"
              onClick={() => setLang("en")}
              aria-pressed={lang === "en"}
              className={`tap-target flex min-w-[44px] items-center justify-center px-3 text-[11px] font-bold uppercase tracking-[0.12em] transition ${
                lang === "en" ? "bg-white text-black" : "text-white/70 hover:text-white"
              }`}
            >
              {c.langEn}
            </button>
          </div>
        </div>

        <div className="flex border-t border-white/[0.06] px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45 lg:hidden">
          <a href="#spotlight" className="tap-target flex-1 py-2 text-center hover:text-white/80">
            {c.navAnchorSpotlight}
          </a>
          <a href="#about" className="tap-target flex-1 border-x border-white/[0.06] py-2 text-center hover:text-white/80">
            {c.navAnchorStory}
          </a>
          <a href="#contact" className="tap-target flex-1 py-2 text-center hover:text-white/80">
            {c.navAnchorVisit}
          </a>
        </div>
      </header>

      <main>
        {/* Hero — full-bleed headline stack */}
        <section
          id="hero"
          aria-labelledby="hero-title"
          className="relative bg-ink text-white"
        >
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_55%_at_50%_110%,rgba(194,65,12,0.18),transparent_55%)]" />
          <div className="relative mx-auto flex min-h-[100svh] max-w-[1600px] flex-col justify-end px-4 pb-16 pt-[calc(8.5rem+var(--safe-top))] md:px-8 md:pb-24 md:pt-32 lg:px-14 lg:pb-32">
            <p className="text-[10px] font-bold uppercase tracking-[0.38em] text-white/45 md:text-[11px]">
              {c.heroKicker}
            </p>
            <h1
              id="hero-title"
              className="font-display mt-5 text-[clamp(2.75rem,13vw,6.25rem)] font-bold leading-[0.94] tracking-tight"
            >
              {c.heroTitle}
              <span className="mt-1 block text-white/82 md:mt-2">{c.heroTitleLine2}</span>
            </h1>
            <p className="mt-8 max-w-lg text-[15px] leading-[1.65] text-white/55 md:mt-10 md:max-w-xl md:text-[17px]">
              {c.heroSubline}
            </p>
            <div className="mt-10 flex flex-wrap gap-3 md:mt-12 md:gap-4">
              <a
                href="#about"
                className="tap-target inline-flex items-center justify-center rounded-full bg-white px-8 text-[12px] font-bold uppercase tracking-[0.18em] text-black transition hover:bg-white/90 md:px-10"
              >
                {c.heroCtaPrimary}
              </a>
              <a
                href="#hours"
                className="tap-target inline-flex items-center justify-center rounded-full border border-white/35 bg-transparent px-8 text-[12px] font-bold uppercase tracking-[0.18em] text-white transition hover:border-white hover:bg-white/[0.06] md:px-10"
              >
                {c.heroCtaSecondary}
              </a>
            </div>
          </div>
        </section>

        {/* Spotlight — three tall panels */}
        <section
          id="spotlight"
          className="scroll-mt-20 bg-fog text-ink"
          aria-labelledby="spotlight-h"
        >
          <div className="mx-auto max-w-[1600px] px-4 py-16 md:px-8 md:py-24 lg:py-28">
            <div className="flex flex-col gap-8 border-b border-neutral-300 pb-10 md:flex-row md:items-end md:justify-between md:pb-14">
              <h2
                id="spotlight-h"
                className="font-display text-[clamp(2rem,6vw,3.5rem)] font-bold uppercase leading-none tracking-tight"
              >
                {c.spotlightLabel}
              </h2>
              <p className="max-w-md text-[14px] leading-relaxed text-neutral-600 md:text-[15px]">
                {c.spotlightSub}
              </p>
            </div>

            <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 lg:gap-4 lg:mt-12">
              {spots.map((spot) => (
                <a
                  key={spot.title}
                  href={spot.hash}
                  className="group relative isolate flex aspect-[4/5] flex-col justify-end overflow-hidden bg-neutral-900 p-6 text-white md:p-8"
                >
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${spot.gradient} opacity-90 transition duration-500 group-hover:scale-105 group-hover:opacity-100`}
                    aria-hidden
                  />
                  <div
                    className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20width=%2240%22%20height=%2240%22%3E%3Cpath%20d=%22M0%2040h40V0%22%20fill=%22none%22%20stroke=%22%23fff%22%20stroke-opacity=%22.04%22/%3E%3C/svg%3E')] opacity-30"
                    aria-hidden
                  />
                  <div className="relative translate-y-2 transition duration-300 group-hover:translate-y-0">
                    <p className="font-display text-2xl font-bold leading-tight tracking-tight md:text-3xl">
                      {spot.title}
                    </p>
                    <p className="mt-3 max-w-[18ch] text-[13px] leading-relaxed text-white/70 md:text-[14px]">
                      {spot.body}
                    </p>
                    <span className="mt-6 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-white group-hover:gap-3">
                      {spot.link}
                      <span aria-hidden>→</span>
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>

        {/* Editorial strip — ambience placeholders */}
        <section
          id="gallery"
          className="scroll-mt-20 bg-white"
          aria-labelledby="gal-h"
        >
          <div className="border-y border-neutral-200">
            <div className="mx-auto max-w-[1600px] px-4 py-10 md:px-8 md:py-14">
              <div className="flex flex-col gap-2 md:flex-row md:items-baseline md:justify-between">
                <h2
                  id="gal-h"
                  className="font-display text-xl font-bold uppercase tracking-tight md:text-2xl"
                >
                  {c.galleryTitle}
                </h2>
                <p className="text-[13px] text-neutral-500 md:max-w-lg md:text-right">{c.galleryCaption}</p>
              </div>
              <div className="mt-8 grid grid-cols-2 gap-1 md:grid-cols-4 md:gap-[2px]">
                {[
                  "from-orange-800/80 to-stone-950",
                  "from-amber-900/90 to-neutral-950",
                  "from-orange-950 to-black",
                  "from-persimmon-800/85 to-neutral-950",
                ].map((g, i) => (
                  <div
                    key={i}
                    className={`relative aspect-[16/10] bg-gradient-to-br ${g} md:aspect-[21/9]`}
                  >
                    <span className="sr-only">{c.galleryCaption}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Values + about — light on white then ink band */}
        <section id="about" className="scroll-mt-20 bg-white" aria-labelledby="about-h">
          <div className="mx-auto max-w-[1600px] px-4 py-16 md:px-8 md:py-20">
            <p className="text-[10px] font-bold uppercase tracking-[0.32em] text-neutral-400">{c.valuesLabel}</p>

            <div className="mt-8 grid gap-10 md:grid-cols-12 md:gap-12">
              <div className="md:col-span-5">
                <h2
                  id="about-h"
                  className="font-display text-2xl font-bold leading-snug tracking-tight text-ink md:text-3xl"
                >
                  {c.aboutTitle}
                </h2>
              </div>
              <div className="md:col-span-7">
                <p className="text-[15px] leading-relaxed text-neutral-600 md:text-[16px]">{c.aboutBody}</p>
                <ul className="mt-10 grid gap-4 border-t border-neutral-200 pt-10 sm:grid-cols-3">
                  {[c.craft1, c.craft2, c.craft3].map((line, i) => (
                    <li key={i} className="relative pl-4 text-[13px] font-medium leading-snug text-neutral-700 before:absolute before:left-0 before:top-1.5 before:h-1.5 before:w-1.5 before:bg-black">
                      {line}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Hours — inverted bar */}
        <section id="hours" className="scroll-mt-20 bg-ink px-4 py-14 text-white md:px-8 md:py-20" aria-labelledby="hours-h">
          <div className="mx-auto grid max-w-[1600px] gap-10 md:grid-cols-12 md:gap-8">
            <div className="md:col-span-4">
              <h2 id="hours-h" className="font-display text-2xl font-bold uppercase tracking-tight md:text-3xl">
                {c.hoursTitle}
              </h2>
              <p className="mt-4 text-[13px] text-white/45">{c.hoursNote}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 md:col-span-8 md:gap-6">
              <div className="border border-white/15 p-6 md:p-8">
                <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/40">{c.weekdays}</p>
                <p className="font-display mt-3 text-3xl font-bold md:text-4xl">07:30 – 18:30</p>
              </div>
              <div className="border border-white/15 p-6 md:p-8">
                <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-white/40">{c.weekend}</p>
                <p className="font-display mt-3 text-3xl font-bold md:text-4xl">08:30 – 19:30</p>
              </div>
              <div className="border border-dashed border-white/25 p-5 sm:col-span-2">
                <p className="font-medium text-white/90">{c.closed}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Visit */}
        <section id="contact" className="scroll-mt-20 bg-fog px-4 py-16 md:px-8 md:py-24" aria-labelledby="con-h">
          <div className="mx-auto grid max-w-[1600px] gap-10 md:grid-cols-2 md:gap-16">
            <h2 id="con-h" className="font-display text-3xl font-bold uppercase tracking-tight md:text-4xl">
              {c.contactTitle}
            </h2>
            <div className="space-y-4 text-[15px] leading-relaxed text-neutral-700">
              <p className="font-medium text-ink">{c.addressLine}</p>
              <p>{c.wechatPlaceholder}</p>
              <p className="text-neutral-500">{c.phonePlaceholder}</p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-ink px-4 py-14 text-white md:px-8">
          <div className="mx-auto flex max-w-[1600px] flex-col gap-10 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="font-display text-lg font-bold uppercase tracking-tight">{c.navBrandFull}</p>
              <p className="mt-3 max-w-sm text-[13px] leading-relaxed text-white/45">
                © {new Date().getFullYear()} {c.navBrandFull}
                <span className="mx-2 text-white/25">·</span>
                {c.footerTiny}
                lava7397.com
              </p>
            </div>
            <a
              href="/home.html"
              className="tap-target inline-flex w-fit items-center border-b border-white pb-1 text-[11px] font-bold uppercase tracking-[0.24em] transition hover:border-white/50 hover:text-white/80"
              aria-label={c.backHomeAria}
            >
              ← {c.backHomeLabel}
            </a>
          </div>
        </footer>
      </main>
    </>
  );
}
