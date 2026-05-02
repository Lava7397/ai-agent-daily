import type { Metadata, Viewport } from "next";
import "./globals.css";
import { copy } from "@/lib/copy";

export const metadata: Metadata = {
  title: copy.zh.metaTitle,
  description: copy.zh.metaDesc,
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#5c2f20",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="font-sans min-h-[100dvh] bg-persimmon-50 text-persimmon-900">{children}</body>
    </html>
  );
}
