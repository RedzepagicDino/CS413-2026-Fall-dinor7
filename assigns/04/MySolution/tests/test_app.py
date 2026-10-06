import unittest, time
from app.reader import read_source
from app import lambda1 as L
from app.backend import LambdaBackend, Kind, Result
from app.model import AppModel
from app.controller import Controller

class ReaderAndLintTests(unittest.TestCase):
 def test_all_key_binding_rules_and_frozenset(self):
  e=read_source('D0Elet("x", D0Evar("x"), D0Elam("y", D0Eop2("+", D0Evar("x"), D0Evar("z"))))')
  got=L.d0exp_fvset(e); self.assertIsInstance(got,frozenset); self.assertEqual(got,frozenset({'x','z'}))
  self.assertEqual(L.d0exp_fvset(read_source('D0Efix("f", "x", D0Eapp(D0Evar("f"),D0Evar("x")))')),frozenset())
 def test_lint_closed_open_and_no_evaluation(self):
  b=LambdaBackend(); self.assertEqual(b.lint('D0Eop2("/",D0Eint(1),D0Eint(0))',1).kind,Kind.SUCCESS)
  r=b.lint('D0Eop2("+",D0Evar("z"),D0Evar("a"))',1); self.assertEqual(r.kind,Kind.INVALID); self.assertIn('a, z',r.text)
 def test_reader_blocks_python(self): self.assertEqual(LambdaBackend().lint('__import__("os").system("x")',1).kind,Kind.INVALID)
class InterpreterTests(unittest.TestCase):
 def test_arithmetic_factorial_fibonacci_and_failures(self):
  b=LambdaBackend(); self.assertIn('42',b.interpret('D0Eop2("+",D0Eint(20),D0Eint(22))',1).text)
  fact='D0Eapp(D0Efix("f","n",D0Eif0(D0Eop2("==",D0Evar("n"),D0Eint(0)),D0Eint(1),D0Eop2("*",D0Evar("n"),D0Eapp(D0Evar("f"),D0Eop2("-",D0Evar("n"),D0Eint(1)))))),D0Eint(5))'
  self.assertIn('120',b.interpret(fact,1).text); self.assertEqual(b.interpret('oops',1).kind,Kind.INVALID); self.assertEqual(b.interpret('D0Eop2("/",D0Eint(1),D0Eint(0))',1).kind,Kind.INVALID)
class ControllerTests(unittest.TestCase):
 def test_replace_invalid_and_dispatch(self):
  m=AppModel(); c=Controller(m,LambdaBackend()); old=m.source
  with self.assertRaises(ValueError): c.change_source('  ')
  self.assertEqual(m.source,old); self.assertEqual(c.act('compile').kind,Kind.UNIMPLEMENTED); self.assertIsNone(m.artifact)
 def test_timeout_retry_with_substitute_backend(self):
  class Slow:
   def lint(self,s,r): time.sleep(.05); return Result('lint',r,Kind.SUCCESS,'ok')
  c=Controller(AppModel(),Slow(),.001); self.assertIn('Timed out',c.act('lint').text)
if __name__=='__main__': unittest.main()
