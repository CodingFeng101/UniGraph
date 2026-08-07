import { expect, test } from '@playwright/test'

test('loads the public application shell without runtime errors', async ({ page }) => {
  const runtimeErrors: string[] = []
  page.on('pageerror', (error) => runtimeErrors.push(error.message))

  const response = await page.goto('/unigraph/login')

  expect(response?.ok()).toBeTruthy()
  await expect(page.locator('#app')).toBeVisible()
  await expect(page.locator('body')).not.toBeEmpty()
  expect(runtimeErrors).toEqual([])
})

test('serves runtime configuration', async ({ request }) => {
  const response = await request.get('/unigraph/config.js')

  expect(response.ok()).toBeTruthy()
  expect(await response.text()).toContain('window.FRONTEND_CONFIG')
  if (process.env.REQUIRE_NGINX_CACHE_HEADERS === '1') {
    expect(response.headers()['cache-control']).toContain('no-store')
  }
})
