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
    symbol: "MSFT",
    name: "Microsoft",
    securityCode: "MS-008",
    aliases: ["마이크로소프트", "azure", "software"],
    sector: "클라우드 소프트웨어",
    exchange: "NASDAQ",
  },
  {
    symbol: "CRWD",
    name: "CrowdStrike",
    securityCode: "CR-007",
    aliases: ["크라우드스트라이크", "보안", "cybersecurity"],
    sector: "사이버보안",
    exchange: "NASDAQ",
  },
  {
    symbol: "005930.KS",
    name: "삼성전자",
    securityCode: "005930",
    aliases: ["samsung electronics", "samsung", "메모리"],
    sector: "반도체",
    exchange: "KRX",
  },
  {
    symbol: "000660.KS",
    name: "SK하이닉스",
    securityCode: "000660",
    aliases: ["sk hynix", "하이닉스", "hbm"],
    sector: "반도체",
    exchange: "KRX",
  },
  {
    symbol: "035420.KS",
    name: "NAVER",
    securityCode: "035420",
    aliases: ["네이버", "search", "commerce"],
    sector: "인터넷",
    exchange: "KRX",
  },
  {
    symbol: "207940.KS",
    name: "삼성바이오로직스",
    securityCode: "207940",
    aliases: ["samsung biologics", "바이오", "cdmo"],
    sector: "바이오",
    exchange: "KRX",
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
    return instrumentCatalog.slice(0, 8);
  }

  return instrumentCatalog.filter((item) =>
    [item.symbol, item.name, item.securityCode, ...item.aliases]
      .join(" ")
      .toLowerCase()
      .includes(normalizedQuery)
  );
}
