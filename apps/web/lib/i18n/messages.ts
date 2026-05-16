export type AppLanguage = "ko" | "en" | "ja" | "zh";

export const appLanguageOptions: Array<{ value: AppLanguage; label: string }> = [
  { value: "ko", label: "한국어" },
  { value: "en", label: "English" },
  { value: "ja", label: "日本語" },
  { value: "zh", label: "中文" },
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
    main: Record<"overview" | "radar" | "stocks" | "history" | "workspace", NavigationCopy>;
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

const sharedSnapshotTone = {
  stanceTone: {
    bullish: "positive",
    neutral: "neutral",
    bearish: "negative",
  },
} satisfies Messages["snapshots"];

export const appMessages: Record<AppLanguage, Messages> = {
  ko: {
    shell: {
      badge: "Market desk",
      title: "Stock Desk",
      description:
        "미국장과 국내장을 한 흐름으로 읽는 주식 리서치 워크스페이스입니다.",
      coverageLabel: "시장",
      coverageValue: "미국 / 한국",
      modeLabel: "초점",
      modeValue: "리서치",
      footerNote: "가격, 뉴스, 공시, 일정, 판단 기록을 한곳에서 확인합니다.",
    },
    topbar: {
      workspaceBadge: "US / KR",
      mobileMenuSr: "메뉴 열기",
      mobileSheetTitle: "Stock Desk",
      mobileSheetDescription: "시장, 레이더, 종목, 기록 화면으로 이동합니다.",
      languagePlaceholder: "언어",
      workflowLabel: "투자 판단 흐름",
    },
    theme: {
      toLight: "밝은 화면",
      toDark: "어두운 화면",
      pending: "화면 모드 변경",
    },
    common: {
      apply: "적용",
      delete: "삭제",
      save: "저장",
      active: "켜짐",
      inactive: "꺼짐",
      none: "없음",
      previous: "이전",
      next: "다음",
      confidence: "신뢰도",
      relatedDate: "관련일",
      expectedSource: "필요한 출처",
      goToLinkedView: "관련 화면 열기",
    },
    navigation: {
      main: {
        overview: {
          label: "시장",
          eyebrow: "오늘의 큰 흐름",
          description: "지수, 섹터, 뉴스, 위험 요인을 먼저 정리합니다.",
        },
        radar: {
          label: "레이더",
          eyebrow: "관심 종목 비교",
          description: "점수, 거래량, 이벤트 기준으로 종목을 빠르게 좁힙니다.",
        },
        stocks: {
          label: "종목",
          eyebrow: "차트와 근거",
          description: "가격, 패턴, 뉴스, 공시, 판단 기록을 종목별로 봅니다.",
        },
        history: {
          label: "기록",
          eyebrow: "과거 반응 복기",
          description: "급등락과 이벤트를 차트 위에서 다시 확인합니다.",
        },
        workspace: {
          label: "워크스페이스",
          eyebrow: "계정과 자동화",
          description: "로그인, 구독, 리포트, 미디어 작업을 관리합니다.",
        },
      },
      auxiliary: {
        news: {
          label: "뉴스",
          eyebrow: "뉴스와 공시",
          description: "시장 뉴스와 국내 공시를 보조 화면에서 확인합니다.",
        },
        calendar: {
          label: "일정",
          eyebrow: "실적과 이벤트",
          description: "실적 발표, 거시 일정, 공시 이벤트를 날짜별로 봅니다.",
        },
      },
    },
    stocks: {
      tabs: {
        score: "판단 점수",
        flow: "수급",
        short: "공매도 / 옵션",
        issues: "뉴스와 공시",
      },
      detail: {
        eyebrow: "종목 분석",
        title: "차트, 이벤트, 지표를 한 화면에서 확인합니다.",
        quickSwitchLabel: "종목 검색",
        quickSwitchHelper: "티커, 회사명, 종목코드로 다른 종목을 바로 열 수 있습니다.",
        currentPrice: "현재가",
        marketCap: "시가총액",
        scoreView: "리서치 점수",
        rulesPresetTitle: "차트 지표",
        rulesPresetDescription:
          "이동평균, 지지선, 거래량 같은 보조 지표를 켜고 끕니다.",
        presetPlaceholder: "프리셋 이름",
        ruleCountSuffix: "개 지표",
        snapshotTitle: "판단 기록",
        snapshotDescription:
          "지금의 판단과 근거를 저장해 나중에 다시 비교합니다.",
        stancePlaceholder: "방향",
        convictionPlaceholder: "확신도",
        snapshotNotePlaceholder:
          "왜 이 방향으로 보는지, 반드시 확인해야 할 위험은 무엇인지 짧게 남겨보세요.",
        snapshotMeta: "선택 이벤트 {event} / 켜진 지표 {count}개",
        viewHistory: "기록에서 보기",
        saveSnapshot: "판단 저장",
        emptySnapshots: "아직 저장된 판단이 없습니다.",
        scoreSummaryTitle: "종합 점수",
        scoreItemSuffix: "점",
        flowSummaryTitle: "수급 요약",
        shortSummaryTitle: "공매도와 옵션",
        issueLink: "자세히 보기",
      },
      stance: {
        bullish: "강세",
        neutral: "중립",
        bearish: "약세",
      },
      conviction: {
        low: "낮음",
        medium: "보통",
        high: "높음",
      },
    },
    history: {
      title: "기록 / 이벤트 복기",
      description: "과거의 큰 움직임을 가격과 이벤트를 함께 보며 다시 읽습니다.",
      searchLabel: "다른 종목 보기",
      searchHelper: "종목을 바꾸면 해당 종목의 이벤트 복기로 이동합니다.",
      rangePlaceholder: "기간",
      customRange: "직접 선택",
      replayTitle: "가격 복기",
      replayFallback: "이벤트를 선택하면 차트가 같은 시점으로 이동합니다.",
      replayHint: "이벤트와 차트를 같은 날짜에 맞춰 봅니다.",
      timelineTitle: "이벤트 타임라인",
      timelineDescription: "뉴스, 공시, 실적 발표를 시간순으로 확인합니다.",
      moveTitle: "움직인 이유",
      moveDescription: "급등과 조정의 배경을 짧게 다시 읽습니다.",
      overlapTitle: "겹친 신호",
      overlapDescription: "전환점 주변에서 함께 나타난 보조 지표입니다.",
      journalTitle: "리서치 기록",
      journalDescription: "저장한 판단을 시간순으로 봅니다.",
      savedCount: (count) => `저장된 기록 ${count}개`,
      goToDetail: "종목 화면 열기",
      journalEmpty: "아직 이 종목에 저장된 판단 기록이 없습니다.",
      tonePositive: "강세",
      toneNegative: "주의",
      toneNeutral: "중립",
    },
    snapshots: sharedSnapshotTone,
  },
  en: {
    shell: {
      badge: "Market desk",
      title: "Stock Desk",
      description:
        "A research workspace for reading US and Korean equities in one flow.",
      coverageLabel: "Markets",
      coverageValue: "US / Korea",
      modeLabel: "Focus",
      modeValue: "Research",
      footerNote: "Prices, news, filings, events, and notes stay connected.",
    },
    topbar: {
      workspaceBadge: "US / KR",
      mobileMenuSr: "Open menu",
      mobileSheetTitle: "Stock Desk",
      mobileSheetDescription: "Move between market, radar, stock, and history views.",
      languagePlaceholder: "Language",
      workflowLabel: "Research flow",
    },
    theme: {
      toLight: "Light mode",
      toDark: "Dark mode",
      pending: "Toggle theme",
    },
    common: {
      apply: "Apply",
      delete: "Delete",
      save: "Save",
      active: "On",
      inactive: "Off",
      none: "None",
      previous: "Previous",
      next: "Next",
      confidence: "Confidence",
      relatedDate: "Related date",
      expectedSource: "Expected source",
      goToLinkedView: "Open related view",
    },
    navigation: {
      main: {
        overview: {
          label: "Market",
          eyebrow: "Today at a glance",
          description: "Start with indices, sectors, headlines, and risk.",
        },
        radar: {
          label: "Radar",
          eyebrow: "Watchlist comparison",
          description: "Narrow names by score, volume, sector, and upcoming events.",
        },
        stocks: {
          label: "Stock",
          eyebrow: "Chart and evidence",
          description: "Review price, patterns, news, filings, and saved notes.",
        },
        history: {
          label: "History",
          eyebrow: "Event replay",
          description: "Replay past moves with the chart and event timeline together.",
        },
        workspace: {
          label: "Workspace",
          eyebrow: "Account and reports",
          description: "Manage login, plans, reports, and media jobs.",
        },
      },
      auxiliary: {
        news: {
          label: "News",
          eyebrow: "News and filings",
          description: "Read market headlines and domestic disclosures.",
        },
        calendar: {
          label: "Calendar",
          eyebrow: "Earnings and events",
          description: "Track earnings, macro events, and disclosures by date.",
        },
      },
    },
    stocks: {
      tabs: {
        score: "Score",
        flow: "Flow",
        short: "Short / Options",
        issues: "News and filings",
      },
      detail: {
        eyebrow: "Stock analysis",
        title: "Read the chart, events, and signals in one view.",
        quickSwitchLabel: "Search stocks",
        quickSwitchHelper: "Jump by ticker, company name, or security code.",
        currentPrice: "Price",
        marketCap: "Market cap",
        scoreView: "Research score",
        rulesPresetTitle: "Chart signals",
        rulesPresetDescription: "Toggle moving averages, support, volume, and risk signals.",
        presetPlaceholder: "Preset name",
        ruleCountSuffix: "signals",
        snapshotTitle: "Decision note",
        snapshotDescription: "Save the current view and compare it later.",
        stancePlaceholder: "Bias",
        convictionPlaceholder: "Conviction",
        snapshotNotePlaceholder: "Write why you hold this view and what still needs checking.",
        snapshotMeta: "Selected event {event} / Active signals {count}",
        viewHistory: "Open history",
        saveSnapshot: "Save note",
        emptySnapshots: "No saved notes yet.",
        scoreSummaryTitle: "Composite score",
        scoreItemSuffix: "pts",
        flowSummaryTitle: "Flow summary",
        shortSummaryTitle: "Short and options",
        issueLink: "Open detail",
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
      description: "Replay why a stock moved with price and events together.",
      searchLabel: "Replay another stock",
      searchHelper: "Changing the symbol opens that stock's replay.",
      rangePlaceholder: "Range",
      customRange: "Custom range",
      replayTitle: "Price replay",
      replayFallback: "Select an event to align the chart.",
      replayHint: "Keep the chart and event timeline on the same date.",
      timelineTitle: "Event timeline",
      timelineDescription: "News, filings, and earnings in time order.",
      moveTitle: "Why it moved",
      moveDescription: "Short reasons behind rallies and pullbacks.",
      overlapTitle: "Overlapping signals",
      overlapDescription: "Supporting signals that appeared near turning points.",
      journalTitle: "Research notes",
      journalDescription: "Saved notes for this symbol in time order.",
      savedCount: (count) => `${count} saved note${count === 1 ? "" : "s"}`,
      goToDetail: "Open stock page",
      journalEmpty: "No saved notes for this symbol yet.",
      tonePositive: "Bullish",
      toneNegative: "Caution",
      toneNeutral: "Neutral",
    },
    snapshots: sharedSnapshotTone,
  },
  ja: {
    shell: {
      badge: "Market desk",
      title: "Stock Desk",
      description: "米国株と韓国株を一つの流れで読むリサーチワークスペースです。",
      coverageLabel: "市場",
      coverageValue: "米国 / 韓国",
      modeLabel: "焦点",
      modeValue: "リサーチ",
      footerNote: "価格、ニュース、開示、予定、判断メモをつなげて確認します。",
    },
    topbar: {
      workspaceBadge: "US / KR",
      mobileMenuSr: "メニューを開く",
      mobileSheetTitle: "Stock Desk",
      mobileSheetDescription: "市場、レーダー、銘柄、履歴画面へ移動します。",
      languagePlaceholder: "言語",
      workflowLabel: "リサーチの流れ",
    },
    theme: {
      toLight: "ライトモード",
      toDark: "ダークモード",
      pending: "表示モードを変更",
    },
    common: {
      apply: "適用",
      delete: "削除",
      save: "保存",
      active: "オン",
      inactive: "オフ",
      none: "なし",
      previous: "前へ",
      next: "次へ",
      confidence: "信頼度",
      relatedDate: "関連日",
      expectedSource: "必要なソース",
      goToLinkedView: "関連画面を開く",
    },
    navigation: {
      main: {
        overview: {
          label: "市場",
          eyebrow: "今日の流れ",
          description: "指数、セクター、ニュース、リスクを先に整理します。",
        },
        radar: {
          label: "レーダー",
          eyebrow: "ウォッチリスト比較",
          description: "スコア、出来高、イベントで銘柄をすばやく絞ります。",
        },
        stocks: {
          label: "銘柄",
          eyebrow: "チャートと根拠",
          description: "価格、パターン、ニュース、開示、メモを銘柄別に見ます。",
        },
        history: {
          label: "履歴",
          eyebrow: "過去反応の復習",
          description: "急騰急落とイベントをチャート上で確認します。",
        },
        workspace: {
          label: "ワークスペース",
          eyebrow: "アカウントとレポート",
          description: "ログイン、プラン、レポート、メディア作業を管理します。",
        },
      },
      auxiliary: {
        news: {
          label: "ニュース",
          eyebrow: "ニュースと開示",
          description: "市場ニュースと韓国開示を確認します。",
        },
        calendar: {
          label: "予定",
          eyebrow: "決算とイベント",
          description: "決算、マクロ、開示イベントを日付別に見ます。",
        },
      },
    },
    stocks: {
      tabs: {
        score: "判断スコア",
        flow: "需給",
        short: "空売り / オプション",
        issues: "ニュースと開示",
      },
      detail: {
        eyebrow: "銘柄分析",
        title: "チャート、イベント、指標を一画面で確認します。",
        quickSwitchLabel: "銘柄検索",
        quickSwitchHelper: "ティッカー、会社名、銘柄コードで移動できます。",
        currentPrice: "現在値",
        marketCap: "時価総額",
        scoreView: "リサーチスコア",
        rulesPresetTitle: "チャート指標",
        rulesPresetDescription: "移動平均、支持線、出来高などの指標を切り替えます。",
        presetPlaceholder: "プリセット名",
        ruleCountSuffix: "指標",
        snapshotTitle: "判断メモ",
        snapshotDescription: "今の判断を保存して後で比較します。",
        stancePlaceholder: "方向",
        convictionPlaceholder: "確信度",
        snapshotNotePlaceholder: "なぜそう見るのか、確認すべきリスクを書きます。",
        snapshotMeta: "選択イベント {event} / 有効指標 {count}",
        viewHistory: "履歴で見る",
        saveSnapshot: "メモを保存",
        emptySnapshots: "保存された判断はまだありません。",
        scoreSummaryTitle: "総合スコア",
        scoreItemSuffix: "点",
        flowSummaryTitle: "需給サマリー",
        shortSummaryTitle: "空売りとオプション",
        issueLink: "詳細を見る",
      },
      stance: {
        bullish: "強気",
        neutral: "中立",
        bearish: "弱気",
      },
      conviction: {
        low: "低い",
        medium: "普通",
        high: "高い",
      },
    },
    history: {
      title: "履歴 / イベント復習",
      description: "過去の大きな動きを価格とイベントで読み直します。",
      searchLabel: "別の銘柄を見る",
      searchHelper: "銘柄を変えるとその銘柄の履歴へ移動します。",
      rangePlaceholder: "期間",
      customRange: "手動選択",
      replayTitle: "価格リプレイ",
      replayFallback: "イベントを選ぶとチャートが同じ時点へ移動します。",
      replayHint: "イベントとチャートを同じ日付で確認します。",
      timelineTitle: "イベントタイムライン",
      timelineDescription: "ニュース、開示、決算を時系列で確認します。",
      moveTitle: "動いた理由",
      moveDescription: "上昇と調整の背景を短く読み直します。",
      overlapTitle: "重なったシグナル",
      overlapDescription: "転換点付近で同時に出た補助指標です。",
      journalTitle: "リサーチメモ",
      journalDescription: "保存した判断を時系列で見ます。",
      savedCount: (count) => `保存済みメモ ${count}件`,
      goToDetail: "銘柄画面を開く",
      journalEmpty: "この銘柄に保存された判断はまだありません。",
      tonePositive: "強気",
      toneNegative: "注意",
      toneNeutral: "中立",
    },
    snapshots: sharedSnapshotTone,
  },
  zh: {
    shell: {
      badge: "Market desk",
      title: "Stock Desk",
      description: "把美股和韩股放在同一流程中阅读的股票研究工作台。",
      coverageLabel: "市场",
      coverageValue: "美国 / 韩国",
      modeLabel: "重点",
      modeValue: "研究",
      footerNote: "价格、新闻、公告、日程和判断记录保持连接。",
    },
    topbar: {
      workspaceBadge: "US / KR",
      mobileMenuSr: "打开菜单",
      mobileSheetTitle: "Stock Desk",
      mobileSheetDescription: "在市场、雷达、个股和历史页面之间切换。",
      languagePlaceholder: "语言",
      workflowLabel: "研究流程",
    },
    theme: {
      toLight: "浅色模式",
      toDark: "深色模式",
      pending: "切换显示模式",
    },
    common: {
      apply: "应用",
      delete: "删除",
      save: "保存",
      active: "开启",
      inactive: "关闭",
      none: "无",
      previous: "上一个",
      next: "下一个",
      confidence: "可信度",
      relatedDate: "相关日期",
      expectedSource: "需要的数据源",
      goToLinkedView: "打开相关页面",
    },
    navigation: {
      main: {
        overview: {
          label: "市场",
          eyebrow: "今日主线",
          description: "先看指数、板块、新闻和风险。",
        },
        radar: {
          label: "雷达",
          eyebrow: "自选股比较",
          description: "按评分、成交量、板块和事件快速筛选。",
        },
        stocks: {
          label: "个股",
          eyebrow: "图表和依据",
          description: "按个股查看价格、形态、新闻、公告和笔记。",
        },
        history: {
          label: "历史",
          eyebrow: "事件复盘",
          description: "在图表上复盘过去的涨跌和事件。",
        },
        workspace: {
          label: "工作台",
          eyebrow: "账户和报告",
          description: "管理登录、套餐、报告和媒体任务。",
        },
      },
      auxiliary: {
        news: {
          label: "新闻",
          eyebrow: "新闻和公告",
          description: "查看市场新闻和韩国公告。",
        },
        calendar: {
          label: "日程",
          eyebrow: "财报和事件",
          description: "按日期追踪财报、宏观事件和公告。",
        },
      },
    },
    stocks: {
      tabs: {
        score: "判断评分",
        flow: "资金流",
        short: "做空 / 期权",
        issues: "新闻和公告",
      },
      detail: {
        eyebrow: "个股分析",
        title: "在一个页面查看图表、事件和信号。",
        quickSwitchLabel: "搜索个股",
        quickSwitchHelper: "用代码、公司名或证券编号快速跳转。",
        currentPrice: "当前价",
        marketCap: "市值",
        scoreView: "研究评分",
        rulesPresetTitle: "图表信号",
        rulesPresetDescription: "切换均线、支撑、成交量和风险信号。",
        presetPlaceholder: "预设名称",
        ruleCountSuffix: "个信号",
        snapshotTitle: "判断记录",
        snapshotDescription: "保存当前观点，之后再比较。",
        stancePlaceholder: "方向",
        convictionPlaceholder: "确信度",
        snapshotNotePlaceholder: "写下你的判断理由和仍需确认的风险。",
        snapshotMeta: "已选事件 {event} / 启用信号 {count}",
        viewHistory: "查看历史",
        saveSnapshot: "保存记录",
        emptySnapshots: "还没有保存的判断记录。",
        scoreSummaryTitle: "综合评分",
        scoreItemSuffix: "分",
        flowSummaryTitle: "资金流摘要",
        shortSummaryTitle: "做空和期权",
        issueLink: "查看详情",
      },
      stance: {
        bullish: "看涨",
        neutral: "中性",
        bearish: "看跌",
      },
      conviction: {
        low: "低",
        medium: "中",
        high: "高",
      },
    },
    history: {
      title: "历史 / 事件复盘",
      description: "把过去的大波动与价格和事件一起重新阅读。",
      searchLabel: "查看其他个股",
      searchHelper: "切换代码后会打开对应个股的事件复盘。",
      rangePlaceholder: "区间",
      customRange: "自定义",
      replayTitle: "价格复盘",
      replayFallback: "选择事件后，图表会移动到同一时间点。",
      replayHint: "让事件和图表对齐到同一日期。",
      timelineTitle: "事件时间线",
      timelineDescription: "按时间查看新闻、公告和财报。",
      moveTitle: "波动原因",
      moveDescription: "简短复盘上涨和回调的背景。",
      overlapTitle: "重叠信号",
      overlapDescription: "转折点附近同时出现的辅助信号。",
      journalTitle: "研究记录",
      journalDescription: "按时间查看保存的判断。",
      savedCount: (count) => `已保存记录 ${count}条`,
      goToDetail: "打开个股页面",
      journalEmpty: "这个个股还没有保存的判断记录。",
      tonePositive: "看涨",
      toneNegative: "注意",
      toneNeutral: "中性",
    },
    snapshots: sharedSnapshotTone,
  },
};

export function getMessages(language: AppLanguage) {
  return appMessages[language] ?? appMessages.ko;
}
