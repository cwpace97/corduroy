import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ColorSchemeScript, MantineProvider, createTheme } from "@mantine/core";
import "@mantine/core/styles.css";
import "@mantine/charts/styles.css";
import "./globals.css";
import { ApolloWrapper } from "@/lib/apollo-provider";
import { MegaHeader } from "@/components/MegaHeader/MegaHeader";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const theme = createTheme({
  primaryColor: 'blue',
  colors: {
    dark: [
      '#C1C2C5',
      '#A6A7AB',
      '#909296',
      '#5C5F66',
      '#373A40',
      '#2C2E33',
      '#25262B',
      '#1A1B1E',
      '#141517',
      '#101113',
    ],
  },
});

export const metadata: Metadata = {
  title: "Tracks Ski",
  description: "Real-time lift and trail status for Colorado ski resorts",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-mantine-color-scheme="dark">
      <head>
        <ColorSchemeScript defaultColorScheme="dark" />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <MantineProvider theme={theme} defaultColorScheme="dark">
          <ApolloWrapper>
            <MegaHeader />
            {children}
          </ApolloWrapper>
        </MantineProvider>
      </body>
    </html>
  );
}
