export type AppLanguage = "ko" | "en";

export const appLanguageOptions: Array<{ value: AppLanguage; label: string }> = [
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
];

type NavigationCopy = {
  label: string;
  eyebrow: string;
  description: string;
};

type SnapshotTone = "bullish" | "neutral" | "bearish";
type ConvictionLevel = "low" | "medium" | "high";

type Messages = {
  shell: {
    badge: string;
    title: string;
    description: string;
    coverageLabel: string;
    coverageValue: string;
    modeLabel: string;
    modeValue: string;
    footerNote: string;
  };
  topbar: {
    workspaceBadge: string;
    mobileMenuSr: string;
    mobileSheetTitle: string;
    mobileSheetDescription: string;
    languagePlaceholder: string;
    workflowLabel: string;
  };
  theme: {
    toLight: string;
    toDark: string;
    pending: string;
  };
  common: {
    apply: string;
    delete: string;
    save: string;
    active: string;
    inactive: string;
    none: string;
    previous: string;
    next: string;
    confidence: string;
    relatedDate: string;
    expectedSource: string;
    goToLinkedView: string;
  };
  navigation: {
    main: Record<"overview" | "radar" | "stocks" | "history", NavigationCopy>;
    auxiliary: Record<"news" | "calendar", NavigationCopy>;
  };
  stocks: {
    tabs: {
      score: string;
      flow: string;
      short: string;
      issues: string;
    };
    detail: {
      eyebrow: string;
      title: string;
      quickSwitchLabel: string;
      quickSwitchHelper: string;
      currentPrice: string;
      marketCap: string;
      scoreView: string;
      rulesPresetTitle: string;
      rulesPresetDescription: string;
      presetPlaceholder: string;
      ruleCountSuffix: string;
      snapshotTitle: string;
      snapshotDescription: string;
      stancePlaceholder: string;
      convictionPlaceholder: string;
      snapshotNotePlaceholder: string;
      snapshotMeta: string;
      viewHistory: string;
      saveSnapshot: string;
      emptySnapshots: string;
      scoreSummaryTitle: string;
      scoreItemSuffix: string;
      flowSummaryTitle: string;
      shortSummaryTitle: string;
      issueLink: string;
    };
    stance: Record<SnapshotTone, string>;
    conviction: Record<ConvictionLevel, string>;
  };
  history: {
    title: string;
    description: string;
    searchLabel: string;
    searchHelper: string;
    rangePlaceholder: string;
    customRange: string;
    replayTitle: string;
    replayFallback: string;
    replayHint: string;
    timelineTitle: string;
    timelineDescription: string;
    moveTitle: string;
    moveDescription: string;
    overlapTitle: string;
    overlapDescription: string;
    journalTitle: string;
    journalDescription: string;
    savedCount: (count: number) => string;
    goToDetail: string;
    journalEmpty: string;
    tonePositive: string;
    toneNegative: string;
    toneNeutral: string;
  };
  snapshots: {
    stanceTone: Record<SnapshotTone, "positive" | "neutral" | "negative">;
  };
};

export const appMessages: Record<AppLanguage, Messages> = {
  ko: {
    shell: {
      badge: "MARKET DESK",
      title: "주식 리서치 데스크",
      description:
        "거시, 섹터, 종목, 히스토리를 하나의 판단 흐름으로 연결하는 리서치 워크스페이스입니다.",
      coverageLabel: "커버리지",
      coverageValue: "미국 · 한국",
      modeLabel: "모드",
      modeValue: "리서치 데스크",
      footerNote: "장식보다 숫자와 리스크를 먼저 봅니다.",
    },
    topbar: {
      workspaceBadge: "US · KR 커버리지",
      mobileMenuSr: "메뉴 열기",
      mobileSheetTitle: "리서치 데스크",
      mobileSheetDescription:
        "핵심 4개 화면을 오가며 시장 판단 흐름을 이어갑니다.",
      languagePlaceholder: "언어",
      workflowLabel: "시장 워크플로우",
    },
    theme: {
      toLight: "라이트 모드로 전환",
      toDark: "다크 모드로 전환",
      pending: "테마 전환",
    },
    common: {
      apply: "적용",
      delete: "삭제",
      save: "저장",
      active: "활성",
      inactive: "보류",
      none: "없음",
      previous: "이전",
      next: "다음",
      confidence: "신뢰도",
      relatedDate: "관련 날짜",
      expectedSource: "예상 출처",
      goToLinkedView: "관련 화면으로 이동",
    },
    navigation: {
      main: {
        overview: {
          label: "오버뷰",
          eyebrow: "시장 판단 시작점",
          description:
            "장 상태, 핵심 지수, 헤드라인, 섹터, 리스크를 한 화면에서 훑습니다.",
        },
        radar: {
          label: "레이더",
          eyebrow: "관심 종목 모니터",
          description:
            "관심 종목 그리드와 섹터별 흐름을 같은 화면에서 비교합니다.",
        },
        stocks: {
          label: "종목 분석",
          eyebrow: "종목 워크스테이션",
          description:
            "차트, 수급, 점수, 옵션, 공매도 단서를 한 종목 중심으로 읽습니다.",
        },
        history: {
          label: "히스토리",
          eyebrow: "이벤트 리플레이",
          description:
            "과거 급등락과 이벤트 반응을 타임라인과 차트로 다시 확인합니다.",
        },
      },
      auxiliary: {
        news: {
          label: "뉴스 피드",
          eyebrow: "뉴스 / 요약",
          description:
            "글로벌 헤드라인, 관심 종목 뉴스, 국내 공시를 보조 화면에서 모읍니다.",
        },
        calendar: {
          label: "이벤트 캘린더",
          eyebrow: "일정 / 실적",
          description:
            "실적, IPO, 국내 공시, 매크로 체크포인트를 일정 기준으로 봅니다.",
        },
      },
    },
    stocks: {
      tabs: {
        score: "점수",
        flow: "수급",
        short: "공매도/옵션",
        issues: "이슈 분석",
      },
      detail: {
        eyebrow: "Stock Workstation",
        title:
          "한 종목의 판단 근거를 차트 중심으로 모아 보는 분석 워크스테이션",
        quickSwitchLabel: "빠른 전환",
        quickSwitchHelper:
          "티커, 종목명, 종목번호 검색으로 다른 종목 워크스테이션으로 이동합니다.",
        currentPrice: "현재가",
        marketCap: "시가총액",
        scoreView: "종합 점수",
        rulesPresetTitle: "사용자 규칙 / preset",
        rulesPresetDescription:
          "보조지표 규칙 조합과 사용자 preset을 저장합니다.",
        presetPlaceholder: "preset 이름",
        ruleCountSuffix: "개 규칙",
        snapshotTitle: "리서치 스냅샷",
        snapshotDescription:
          "현재 판단과 메모를 저장해 /history에서 다시 읽습니다.",
        stancePlaceholder: "판단 방향",
        convictionPlaceholder: "확신도",
        snapshotNotePlaceholder:
          "왜 지금 이 방향으로 보는지, 확인할 리스크가 무엇인지 간단히 남깁니다.",
        snapshotMeta: "선택 이벤트 {event} · 활성 규칙 {count}개",
        viewHistory: "히스토리에서 보기",
        saveSnapshot: "스냅샷 저장",
        emptySnapshots:
          "아직 저장된 판단 기록이 없습니다. 메모를 남기면 /history에서 시점별 판단을 다시 읽을 수 있습니다.",
        scoreSummaryTitle: "종합 점수",
        scoreItemSuffix: "점",
        flowSummaryTitle: "수급 요약",
        shortSummaryTitle: "공매도/옵션 비율",
        issueLink: "관련 화면으로 이동",
      },
      stance: {
        bullish: "강세",
        neutral: "중립",
        bearish: "약세",
      },
      conviction: {
        low: "낮음",
        medium: "중간",
        high: "높음",
      },
    },
    history: {
      title: "히스토리 / 이벤트 리플레이",
      description:
        "종목과 날짜 범위를 바꾸면서 과거 급등·급락 이유를 차트 중심으로 다시 읽습니다.",
      searchLabel: "기록 다시 보기",
      searchHelper:
        "종목을 바꾸면 해당 종목의 이벤트 리플레이로 바로 이동합니다.",
      rangePlaceholder: "구간",
      customRange: "직접 선택",
      replayTitle: "과거 차트 리플레이",
      replayFallback:
        "과거 변곡점을 선택하면 차트와 타임라인이 동시에 이동합니다.",
      replayHint: "이벤트를 고르면 차트와 타임라인이 같은 시점으로 맞춰집니다.",
      timelineTitle: "이벤트 / 뉴스 타임라인",
      timelineDescription: "특정 이벤트를 누르면 차트 시점이 바로 이동합니다.",
      moveTitle: "급등 / 급락 이유 요약",
      moveDescription: "과거 움직임 이유를 카드로 다시 읽습니다.",
      overlapTitle: "중복 지표 설명 카드",
      overlapDescription: "변곡점에서 겹친 보조지표 신호를 함께 봅니다.",
      journalTitle: "리서치 저널",
      journalDescription:
        "현재 종목 기준 저장된 판단 스냅샷을 시점 순으로 다시 읽습니다.",
      savedCount: (count) => `저장된 기록 ${count}건`,
      goToDetail: "상세 화면으로 이동",
      journalEmpty:
        "아직 이 종목에 저장된 판단 기록이 없습니다. /stocks/[symbol] 화면에서 스냅샷을 저장하면 과거 이벤트 리플레이와 함께 회고할 수 있습니다.",
      tonePositive: "강세",
      toneNegative: "주의",
      toneNeutral: "중립",
    },
    snapshots: {
      stanceTone: {
        bullish: "positive",
        neutral: "neutral",
        bearish: "negative",
      },
    },
  },
  en: {
    shell: {
      badge: "MARKET DESK",
      title: "Stock Research Desk",
      description:
        "A working research desk that connects macro, sector, stock, and replay views in one decision flow.",
      coverageLabel: "Coverage",
      coverageValue: "US · KR",
      modeLabel: "Mode",
      modeValue: "Research Desk",
      footerNote: "Start with numbers and risk, not decoration.",
    },
    topbar: {
      workspaceBadge: "US · KR Coverage",
      mobileMenuSr: "Open menu",
      mobileSheetTitle: "Research Desk",
      mobileSheetDescription:
        "Move across the four core views without breaking the market research workflow.",
      languagePlaceholder: "Language",
      workflowLabel: "Market workflow",
    },
    theme: {
      toLight: "Switch to light mode",
      toDark: "Switch to dark mode",
      pending: "Toggle theme",
    },
    common: {
      apply: "Apply",
      delete: "Delete",
      save: "Save",
      active: "Active",
      inactive: "Off",
      none: "None",
      previous: "Previous",
      next: "Next",
      confidence: "Confidence",
      relatedDate: "Related date",
      expectedSource: "Expected source",
      goToLinkedView: "Open linked view",
    },
    navigation: {
      main: {
        overview: {
          label: "Overview",
          eyebrow: "Market Start Point",
          description:
            "Open the desk with market status, indices, headlines, sectors, and risk in one place.",
        },
        radar: {
          label: "Radar",
          eyebrow: "Watchlist Monitor",
          description:
            "Compare your watchlist grid and sector flow on one working screen.",
        },
        stocks: {
          label: "Stock Analysis",
          eyebrow: "Stock Workstation",
          description:
            "Read charts, flow, score, options, and short interest in a chart-first workflow.",
        },
        history: {
          label: "History",
          eyebrow: "Event Replay",
          description:
            "Replay sharp moves and event reactions with a linked timeline and chart.",
        },
      },
      auxiliary: {
        news: {
          label: "News Feed",
          eyebrow: "News / Summary",
          description:
            "A supporting screen that gathers global headlines, watchlist news, and domestic disclosures.",
        },
        calendar: {
          label: "Event Calendar",
          eyebrow: "Schedule / Earnings",
          description:
            "View earnings, IPOs, domestic disclosures, and macro checkpoints in one place.",
        },
      },
    },
    stocks: {
      tabs: {
        score: "Score",
        flow: "Flow",
        short: "Short / Options",
        issues: "Issue Analysis",
      },
      detail: {
        eyebrow: "Stock Workstation",
        title:
          "A focused workstation that brings one stock's decision context into a chart-first view.",
        quickSwitchLabel: "Quick switch",
        quickSwitchHelper:
          "Search by symbol, company name, or security code to jump to another stock workstation.",
        currentPrice: "Price",
        marketCap: "Market Cap",
        scoreView: "Research Score",
        rulesPresetTitle: "User Rules / Presets",
        rulesPresetDescription:
          "Save reusable indicator rule combinations and presets.",
        presetPlaceholder: "Preset name",
        ruleCountSuffix: "rules",
        snapshotTitle: "Research Snapshot",
        snapshotDescription:
          "Save the current thesis and note, then review it again from /history.",
        stancePlaceholder: "Bias",
        convictionPlaceholder: "Conviction",
        snapshotNotePlaceholder:
          "Add a short note on why you hold this bias and which risks still need confirmation.",
        snapshotMeta: "Selected event {event} · Active rules {count}",
        viewHistory: "Open in history",
        saveSnapshot: "Save snapshot",
        emptySnapshots:
          "No decision snapshots saved yet. Save one here and review the thesis again from /history.",
        scoreSummaryTitle: "Composite Score",
        scoreItemSuffix: "pts",
        flowSummaryTitle: "Flow Summary",
        shortSummaryTitle: "Short / Options Mix",
        issueLink: "Open linked view",
      },
      stance: {
        bullish: "Bullish",
        neutral: "Neutral",
        bearish: "Bearish",
      },
      conviction: {
        low: "Low",
        medium: "Medium",
        high: "High",
      },
    },
    history: {
      title: "History / Event Replay",
      description:
        "Change the symbol and date range to replay why a stock moved sharply in the past.",
      searchLabel: "Replay another symbol",
      searchHelper:
        "Changing the symbol jumps directly into that symbol's event replay timeline.",
      rangePlaceholder: "Range",
      customRange: "Custom range",
      replayTitle: "Price Replay",
      replayFallback:
        "Pick a past inflection point and the chart and timeline move together.",
      replayHint: "Choose an event to align the chart and timeline to the same moment.",
      timelineTitle: "Event / News Timeline",
      timelineDescription: "Selecting an event jumps the chart to that date.",
      moveTitle: "Why It Moved",
      moveDescription: "Re-read the reasons behind sharp rallies and pullbacks.",
      overlapTitle: "Indicator Overlap",
      overlapDescription: "See which supporting signals overlapped near turning points.",
      journalTitle: "Research Journal",
      journalDescription:
        "Read back saved decision snapshots for the current symbol in time order.",
      savedCount: (count) => `${count} saved snapshot${count === 1 ? "" : "s"}`,
      goToDetail: "Open stock detail",
      journalEmpty:
        "No saved snapshots exist for this symbol yet. Save one from /stocks/[symbol] and review it alongside the replay.",
      tonePositive: "Bullish",
      toneNegative: "Caution",
      toneNeutral: "Neutral",
    },
    snapshots: {
      stanceTone: {
        bullish: "positive",
        neutral: "neutral",
        bearish: "negative",
      },
    },
  },
};

export function getMessages(language: AppLanguage) {
  return appMessages[language] ?? appMessages.ko;
}
