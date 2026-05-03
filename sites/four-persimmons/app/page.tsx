"use client";

import { useEffect, useState } from "react";
import { MerchantPhoto } from "@/components/MerchantPhoto";
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
      gradient: "from-amber-600/95 via-orange-950/95 to-cocoa",
      hash: "#about",
      photo: "spot-1.webp",
    },
    {
      title: c.spot2Title,
      body: c.spot2Body,
      link: c.spot2Cta,
      gradient: "from-orange-500/90 via-persimmon-900/98 to-cocoa",
      hash: "#gallery",
      photo: "spot-2.webp",
    },
    {
      title: c.spot3Title,
      body: c.spot3Body,
      link: c.spot3Cta,
      gradient: "from-red-900/85 via-persimmon-900 to-cocoa",
      hash: "#contact",
      photo: "spot-3.webp",
    },
  ] as const;

  const galleryGrads = [
    "from-amber-500/85 to-orange-950",
    "from-orange-600/88 to-persimmon-900",
    "from-persimmon-500/82 to-red-950",
    "from-amber-700/82 to-cocoa",
  ];

  const galleryFiles = ["gallery-1.webp", "gallery-2.webp", "gallery-3.webp", "gallery-4.webp"];

  return (
    <>
      <header className="fixed inset-x-0 top-0 z-50 border-b border-amber-900/40 bg-cocoa/98 text-cream-50 backdrop-blur-md supports-[backdrop-filter]:bg-cocoa/95">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-3 pt-[calc(0.75rem+var(--safe-top))] md:px-8">
          <div className="flex min-w-0 flex-1 items-center gap-2">
            <span className="font-display truncate text-lg font-bold uppercase tracking-tighter text-white md:text-xl">
              {c.navBrandShort}
            </span>
            <span className="hidden text-amber-300/60 md:inline">/</span>
            <span className="hidden truncate font-display text-sm font-medium text-amber-100 sm:inline">
              {c.navBrandFull}
            </span>
          </div>

          <nav
            className="hidden items-center gap-7 text-[13px] font-medium uppercase tracking-[0.14em] text-amber-100 lg:flex"
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
            className="flex shrink-0 items-center gap-2 border border-amber-700/60 bg-black/25 p-1"
            role="group"
            aria-label={c.langAria}
          >
            <button
              type="button"
              onClick={() => setLang("zh")}
              aria-pressed={lang === "zh"}
              className={`tap-target flex min-w-[44px] items-center justify-center px-3 text-[11px] font-bold uppercase tracking-[0.12em] transition ${
                lang === "zh"
                  ? "bg-orange-50 text-cocoa shadow-sm"
                  : "text-amber-100 hover:text-white"
              }`}
            >
              {c.langZh}
            </button>
            <button
              type="button"
              onClick={() => setLang("en")}
              aria-pressed={lang === "en"}
              className={`tap-target flex min-w-[44px] items-center justify-center px-3 text-[11px] font-bold uppercase tracking-[0.12em] transition ${
                lang === "en"
                  ? "bg-orange-50 text-cocoa shadow-sm"
                  : "text-amber-100 hover:text-white"
              }`}
            >
              {c.langEn}
            </button>
          </div>
        </div>

        <div className="flex border-t border-amber-900/35 px-4 py-2 text-[11px] font-semibold uppercase tracking-[0.22em] text-amber-100 lg:hidden">
          <a href="#spotlight" className="tap-target flex-1 py-2 text-center hover:text-white">
            {c.navAnchorSpotlight}
          </a>
          <a
            href="#about"
            className="tap-target flex-1 border-x border-amber-950/25 py-2 text-center hover:text-white"
          >
            {c.navAnchorStory}
          </a>
          <a href="#contact" className="tap-target flex-1 py-2 text-center hover:text-white">
            {c.navAnchorVisit}
          </a>
        </div>
      </header>

      <main>
        <section id="hero" aria-labelledby="hero-title" className="relative overflow-hidden bg-cocoa text-cream-50">
          <div className="absolute inset-0">
            <MerchantPhoto filename="hero.webp" alt="" className="h-full w-full object-cover opacity-[0.35]" />
            <div className="absolute inset-0 bg-gradient-to-br from-orange-950/92 via-persimmon-950/90 to-cocoa" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_90%_60%_at_70%_20%,rgba(251,146,60,0.22),transparent_55%)]" />
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_20%_90%,rgba(234,88,12,0.18),transparent_50%)]" />
          </div>

          <div className="relative mx-auto flex min-h-[100svh] max-w-[1600px] flex-col justify-end px-4 pb-16 pt-[calc(8.5rem+var(--safe-top))] md:px-8 md:pb-24 md:pt-32 lg:px-14 lg:pb-32">
            <p className="text-on-dark text-[10px] font-bold uppercase tracking-[0.38em] text-amber-100 md:text-[11px]">
              {c.heroKicker}
            </p>
            <h1
              id="hero-title"
              className="text-on-dark font-display mt-5 text-[clamp(2.75rem,13vw,6.25rem)] font-bold leading-[0.94] tracking-tight text-white"
            >
              {c.heroTitle}
              <span className="mt-1 block text-amber-50 md:mt-2">{c.heroTitleLine2}</span>
            </h1>
            <p className="text-on-dark mt-8 max-w-lg text-[15px] leading-[1.65] text-orange-50/92 md:mt-10 md:max-w-xl md:text-[17px]">
              {c.heroSubline}
            </p>
            <div className="mt-10 flex flex-wrap gap-3 md:mt-12 md:gap-4">
              <a
                href="#about"
                className="tap-target inline-flex items-center justify-center rounded-full bg-orange-50 px-8 text-[12px] font-bold uppercase tracking-[0.18em] text-cocoa transition hover:bg-white md:px-10"
              >
                {c.heroCtaPrimary}
              </a>
              <a
                href="#hours"
                className="tap-target inline-flex items-center justify-center rounded-full border-2 border-white/80 bg-black/20 px-8 text-[12px] font-bold uppercase tracking-[0.18em] text-white backdrop-blur-[2px] transition hover:border-white hover:bg-black/35 md:px-10"
              >
                {c.heroCtaSecondary}
              </a>
            </div>
          </div>
        </section>

        <section
          id="spotlight"
          className="scroll-mt-20 bg-fog text-ink"
          aria-labelledby="spotlight-h"
        >
          <div className="mx-auto max-w-[1600px] px-4 py-16 md:px-8 md:py-24 lg:py-28">
            <div className="flex flex-col gap-8 border-b border-persimmon-300/90 pb-10 md:flex-row md:items-end md:justify-between md:pb-14">
              <h2
                id="spotlight-h"
                className="font-display text-[clamp(2rem,6vw,3.5rem)] font-bold uppercase leading-none tracking-tight text-persimmon-950"
              >
                {c.spotlightLabel}
              </h2>
              <p className="max-w-md text-[14px] leading-relaxed text-neutral-800 md:text-[15px]">
                {c.spotlightSub}
              </p>
            </div>

            <div className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 lg:mt-12 lg:gap-4">
              {spots.map((spot) => (
                <a
                  key={spot.title}
                  href={spot.hash}
                  className="group relative isolate flex aspect-[4/5] flex-col justify-end overflow-hidden bg-orange-950 p-6 text-cream-50 md:p-8"
                >
                  <MerchantPhoto
                    filename={spot.photo}
                    alt=""
                    className="absolute inset-0 z-0 h-full w-full object-cover opacity-50 transition duration-700 group-hover:scale-105 group-hover:opacity-60"
                  />
                  <div
                    className={`absolute inset-0 z-[1] bg-gradient-to-br ${spot.gradient}`}
                    aria-hidden
                  />
                  <div className="absolute inset-0 z-[1] bg-black/40" aria-hidden />
                  <div
                    className="absolute inset-0 z-[1] bg-gradient-to-t from-black/85 via-black/35 to-black/10"
                    aria-hidden
                  />
                  <div
                    className="absolute inset-0 z-[2] bg-[url('data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22%20width=%2240%22%20height=%2240%22%3E%3Cpath%20d=%22M0%2040h40V0%22%20fill=%22none%22%20stroke=%22%23fff%22%20stroke-opacity=%22.06%22/%3E%3C/svg%3E')] opacity-20"
                    aria-hidden
                  />
                  <div className="relative z-10 translate-y-2 transition duration-300 group-hover:translate-y-0">
                    <p className="text-on-dark font-display text-2xl font-bold leading-tight tracking-tight text-white md:text-3xl">
                      {spot.title}
                    </p>
                    <p className="text-on-dark mt-3 max-w-[20ch] text-[13px] leading-relaxed text-orange-50/95 md:text-[14px]">
                      {spot.body}
                    </p>
                    <span className="text-on-dark mt-6 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.2em] text-amber-100 group-hover:gap-3">
                      {spot.link}
                      <span aria-hidden>→</span>
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section id="gallery" className="scroll-mt-20 bg-cream-50" aria-labelledby="gal-h">
          <div className="border-y border-persimmon-200/70">
            <div className="mx-auto max-w-[1600px] px-4 py-10 md:px-8 md:py-14">
              <div className="flex flex-col gap-2 md:flex-row md:items-baseline md:justify-between">
                <h2
                  id="gal-h"
                  className="font-display text-xl font-bold uppercase tracking-tight text-persimmon-950 md:text-2xl"
                >
                  {c.galleryTitle}
                </h2>
                <p className="text-[13px] text-neutral-700 md:max-w-lg md:text-right">{c.galleryCaption}</p>
              </div>
              <p className="mt-4 max-w-3xl text-[12px] leading-relaxed text-neutral-600">{c.assetsNote}</p>
              <div className="mt-8 grid grid-cols-2 gap-1 md:grid-cols-4 md:gap-[2px]">
                {galleryGrads.map((g, i) => (
                  <div
                    key={i}
                    className={`relative aspect-[16/10] overflow-hidden bg-gradient-to-br ${g} md:aspect-[21/9]`}
                  >
                    <MerchantPhoto
                      filename={galleryFiles[i] ?? `gallery-${i + 1}.webp`}
                      alt=""
                      className="absolute inset-0 z-10 h-full w-full object-cover"
                    />
                    <span className="sr-only">{c.galleryCaption}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="about" className="scroll-mt-20 bg-cream-100" aria-labelledby="about-h">
          <div className="mx-auto max-w-[1600px] px-4 py-16 md:px-8 md:py-20">
            <p className="text-[10px] font-bold uppercase tracking-[0.32em] text-persimmon-800">{c.valuesLabel}</p>

            <div className="mt-8 grid gap-10 md:grid-cols-12 md:gap-12">
              <div className="md:col-span-5">
                <h2
                  id="about-h"
                  className="font-display text-2xl font-bold leading-snug tracking-tight text-persimmon-950 md:text-3xl"
                >
                  {c.aboutTitle}
                </h2>
              </div>
              <div className="md:col-span-7">
                <p className="text-[15px] leading-relaxed text-neutral-800 md:text-[16px]">{c.aboutBody}</p>
                <ul className="mt-10 grid gap-4 border-t border-persimmon-300/80 pt-10 sm:grid-cols-3">
                  {[c.craft1, c.craft2, c.craft3].map((line, i) => (
                    <li
                      key={i}
                      className="relative pl-4 text-[13px] font-medium leading-snug text-neutral-800 before:absolute before:left-0 before:top-1.5 before:h-1.5 before:w-1.5 before:rounded-sm before:bg-persimmon-600"
                    >
                      {line}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        <section
          id="hours"
          className="scroll-mt-20 bg-gradient-to-b from-persimmon-950 to-cocoa px-4 py-14 text-cream-50 md:px-8 md:py-20"
          aria-labelledby="hours-h"
        >
          <div className="mx-auto grid max-w-[1600px] gap-10 md:grid-cols-12 md:gap-8">
            <div className="md:col-span-4">
              <h2
                id="hours-h"
                className="font-display text-2xl font-bold uppercase tracking-tight text-white md:text-3xl"
              >
                {c.hoursTitle}
              </h2>
              <p className="mt-4 text-[13px] leading-relaxed text-amber-100/90">{c.hoursNote}</p>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 md:col-span-8 md:gap-6">
              <div className="border border-amber-400/35 bg-black/30 p-6 md:p-8">
                <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-amber-200/90">{c.weekdays}</p>
                <p className="font-display mt-3 text-3xl font-bold text-white md:text-4xl">07:30 – 18:30</p>
              </div>
              <div className="border border-amber-400/35 bg-black/30 p-6 md:p-8">
                <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-amber-200/90">{c.weekend}</p>
                <p className="font-display mt-3 text-3xl font-bold text-white md:text-4xl">08:30 – 19:30</p>
              </div>
              <div className="border border-dashed border-amber-300/50 bg-black/25 p-5 sm:col-span-2">
                <p className="font-medium text-amber-50">{c.closed}</p>
              </div>
            </div>
          </div>
        </section>

        <section id="contact" className="scroll-mt-20 bg-fog px-4 py-16 md:px-8 md:py-24" aria-labelledby="con-h">
          <div className="mx-auto grid max-w-[1600px] gap-10 md:grid-cols-2 md:gap-16">
            <h2
              id="con-h"
              className="font-display text-3xl font-bold uppercase tracking-tight text-persimmon-950 md:text-4xl"
            >
              {c.contactTitle}
            </h2>
            <div className="space-y-4 text-[15px] leading-relaxed text-neutral-800">
              <p className="font-semibold text-ink">{c.addressLine}</p>
              <p>{c.wechatPlaceholder}</p>
              <p className="text-neutral-600">{c.phonePlaceholder}</p>
            </div>
          </div>
        </section>

        <footer className="border-t border-amber-950/30 bg-cocoa px-4 py-14 text-cream-100 md:px-8">
          <div className="mx-auto flex max-w-[1600px] flex-col gap-10 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="font-display text-lg font-bold uppercase tracking-tight text-white">{c.navBrandFull}</p>
              <p className="mt-3 max-w-sm text-[13px] leading-relaxed text-amber-100/80">
                © {new Date().getFullYear()} {c.navBrandFull}
                <span className="mx-2 text-amber-200/45">·</span>
                {c.footerTiny}
                lava7397.com
              </p>
            </div>
            <a
              href="/home.html"
              className="tap-target inline-flex w-fit items-center border-b-2 border-amber-200/70 pb-1 text-[11px] font-bold uppercase tracking-[0.24em] text-amber-50 transition hover:border-white hover:text-white"
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
