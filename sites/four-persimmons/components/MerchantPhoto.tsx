"use client";

import { useState } from "react";

/** Static site is served at /shizi; files from public/bakery/ → /shizi/bakery/ */
const BASE = "/shizi";

export function MerchantPhoto({
  filename,
  alt,
  className,
}: {
  filename: string;
  alt: string;
  className?: string;
}) {
  const [hide, setHide] = useState(false);
  if (hide) return null;
  return (
    <img
      src={`${BASE}/bakery/${filename}`}
      alt={alt}
      className={className}
      loading="lazy"
      decoding="async"
      onError={() => setHide(true)}
    />
  );
}
