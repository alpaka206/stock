import type { InstrumentCatalogItem } from "@/lib/research/types";

export const instrumentCatalog: InstrumentCatalogItem[] = [
  {
    symbol: "NVDA",
    name: "NVIDIA",
    securityCode: "NV-001",
    aliases: ["엔비디아", "gpu", "ai leader"],
    sector: "반도체",
    exchange: "NASDAQ",
  },
  {
    symbol: "AVGO",
    name: "Broadcom",
    securityCode: "AV-002",
    aliases: ["브로드컴", "network", "custom ai"],
    sector: "반도체",
    exchange: "NASDAQ",
  },
  {
    symbol: "VRT",
    name: "Vertiv",
    securityCode: "VR-003",
    aliases: ["버티브", "전력", "data center power"],
    sector: "전력 인프라",
    exchange: "NYSE",
  },
  {
    symbol: "AMD",
    name: "AMD",
    securityCode: "AM-004",
    aliases: ["에이엠디", "mi300", "반도체"],
    sector: "반도체",
    exchange: "NASDAQ",
  },
  {
    symbol: "SMCI",
    name: "Super Micro Computer",
    securityCode: "SM-005",
    aliases: ["슈퍼마이크로", "server", "서버"],
    sector: "서버",
    exchange: "NASDAQ",
  },
  {
    symbol: "PANW",
    name: "Palo Alto Networks",
    securityCode: "PA-006",
    aliases: ["팔로알토", "보안", "security"],
    sector: "사이버보안",
    exchange: "NASDAQ",
  },
  {
    symbol: "CRWD",
    name: "CrowdStrike",
    securityCode: "CR-007",
    aliases: ["크라우드스트라이크", "보안", "crowdstrike"],
    sector: "사이버보안",
    exchange: "NASDAQ",
  },
  {
    symbol: "MSFT",
    name: "Microsoft",
    securityCode: "MS-008",
    aliases: ["마이크로소프트", "azure", "소프트웨어"],
    sector: "소프트웨어",
    exchange: "NASDAQ",
  },
];

export function findInstrument(query: string) {
  const normalizedQuery = query.trim().toLowerCase();

  return instrumentCatalog.find((item) => {
    return [item.symbol, item.name, item.securityCode, ...item.aliases]
      .join(" ")
      .toLowerCase()
      .includes(normalizedQuery);
  });
}

export function filterInstruments(query: string) {
  const normalizedQuery = query.trim().toLowerCase();

  if (!normalizedQuery) {
    return instrumentCatalog.slice(0, 6);
  }

  return instrumentCatalog.filter((item) =>
    [item.symbol, item.name, item.securityCode, ...item.aliases]
      .join(" ")
      .toLowerCase()
      .includes(normalizedQuery)
  );
}
