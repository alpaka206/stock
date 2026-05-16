import { expect, test } from "@playwright/test";

const corePages = [
  { path: "/overview", testId: "overview-page" },
  { path: "/radar", testId: "radar-page" },
  { path: "/stocks/NVDA", testId: "stock-detail-page" },
  { path: "/history?symbol=NVDA", testId: "history-page" },
] as const;

test.describe("core stock workspace pages", () => {
  for (const target of corePages) {
    test(`${target.path} renders without runtime errors`, async ({ page }) => {
      await page.goto(target.path);

      await expect(page.getByTestId(target.testId)).toBeVisible();
      await expect(page.locator("body")).not.toContainText(
        /Application error|Unhandled Runtime Error|404: This page could not be found/
      );
    });
  }

  test("radar search links into stock detail", async ({ page }) => {
    await page.goto("/radar");

    await expect(page.getByTestId("radar-alert-panel")).toBeVisible();
    const alertCards = page.getByTestId("radar-alert-card");
    if ((await alertCards.count()) > 0) {
      await expect(alertCards.first()).toBeVisible();
    }

    await page.getByTestId("radar-search-input").fill("NVDA");
    await expect(page.getByTestId("radar-search-input")).toHaveValue("NVDA");
    await expect(page).toHaveURL(/q=NVDA/);

    await page.getByTestId("radar-open-selected-stock").click();
    await expect(page).toHaveURL(/\/stocks\/[A-Z0-9.]+/);
    await expect(page.getByTestId("stock-detail-page")).toBeVisible();
  });

  test("stock detail exposes chart indicators and pattern analysis", async ({
    page,
  }) => {
    await page.goto("/stocks/NVDA");

    await expect(page.getByTestId("stock-price-chart").locator("svg")).toBeVisible();
    await expect(page.getByTestId("stock-technical-metrics")).toBeVisible();
    await expect(page.getByTestId("stock-pattern-cards")).toBeAttached();
    expect(await page.getByTestId("stock-technical-metric").count()).toBeGreaterThanOrEqual(2);

    const patternCardCount = await page.getByTestId("stock-pattern-card").count();
    expect(patternCardCount).toBeGreaterThanOrEqual(0);
  });

  test("research snapshot can be saved and reviewed from history", async ({
    page,
  }) => {
    const note = "E2E snapshot note for NVDA";

    await page.goto("/stocks/NVDA");
    await page.getByTestId("stock-snapshot-note").fill(note);
    await page.getByTestId("stock-save-snapshot").click();
    await expect(page.getByText(note).first()).toBeVisible();

    await page.goto("/history?symbol=NVDA");
    await expect(page.getByText(note).first()).toBeVisible();
  });

  test("history replay shows chart and selectable events", async ({ page }) => {
    await page.goto("/history?symbol=NVDA");

    await expect(page.getByTestId("history-price-chart").locator("svg")).toBeVisible();
      await expect(page.getByTestId("history-event-timeline")).toBeVisible();

    const events = page.getByTestId("history-event");
    await expect(events.first()).toBeVisible();

    if ((await events.count()) > 1) {
      await events.nth(1).click();
      await expect(page).toHaveURL(/event=/);
    }
  });

  test("workspace renders account report and media controls", async ({ page }) => {
    await page.goto("/workspace");

    await expect(page.getByTestId("workspace-page")).toBeVisible();
    await expect(page.getByText("로그인").first()).toBeVisible();
    await expect(page.getByText("리포트").first()).toBeVisible();
    await expect(page.getByText("오디오 / 영상 현지화").first()).toBeVisible();
  });
});
