import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Stock Desk",
    short_name: "Stock Desk",
    description:
      "미국장과 국내장을 함께 읽는 주식 리서치 워크스페이스",
    start_url: "/overview",
    display: "standalone",
    background_color: "#f7f9fb",
    theme_color: "#0f4c81",
    icons: [
      {
        src: "/icon.svg",
        sizes: "64x64",
        type: "image/svg+xml",
      },
      {
        src: "/apple-icon.svg",
        sizes: "180x180",
        type: "image/svg+xml",
      },
    ],
  };
}
