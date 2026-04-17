---
paths: ["frontend/**/*.test.*"]
---

**Testing**
- Unit test pure logic (score calculation helpers, formatting) with Vitest
- Component tests with React Testing Library + jsdom: render components, interact with them and assert what is visible. Mock API calls. This is the primary way to verify component behaviour.
- Smoke tests with Playwright live in `e2e/` at the repo root — they are a full-stack concern, not part of this package.
- Component tests follow BDD style using `describe`/`it`/`beforeEach` with `givenX`, `whenX`, `thenX` helper functions scoped inside the `describe` block. Example:
  ```typescript
  describe('ScoreCard', () => {
    it('shows filled categories as disabled', () => {
      givenScoreCard({ ones: 3 })
      thenCategoryIsDisabled('ones')
    })

    function givenScoreCard(scores, props = {}) {
      render(<ScoreCard scores={scores} {...props} />)
    }

    function thenCategoryIsDisabled(name: string) {
      expect(screen.getByRole('button', { name })).toBeDisabled()
    }
  })
  ```
