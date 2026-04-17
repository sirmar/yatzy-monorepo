---
paths: ["backend/tests/**", "auth/tests/**"]
---

**Testing**
- Unit tests follow BDD style: a test class per subject, `setup_method` for mock setup, then test methods, then shared `GivenX`, `WhenX`, `ThenX` methods in that order. Results are stored as `self` fields, not passed as parameters. The specific values being tested must appear in the test method body as arguments to Given/When/Then — not hardcoded inside the helpers. Example:
  ```python
  class TestFoo:
    def setup_method(self):
      self.dep = MagicMock()
      self.foo = Foo(self.dep)

    def test_something(self):
      self.GivenDepReturns('expected')
      self.WhenSomethingHappensWith('input')
      self.ThenResultIs('expected')

    def GivenDepReturns(self, value):
      self.dep.get.return_value = value

    def WhenSomethingHappensWith(self, value):
      self.result = self.foo.do_something(value)

    def ThenResultIs(self, value):
      assert self.result == value
  ```
