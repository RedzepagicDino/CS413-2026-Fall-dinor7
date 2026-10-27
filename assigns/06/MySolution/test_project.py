import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "05"))
import unittest
from lambda1_vp import *
from target import *
from compiler import compile_expr, CompileError
from evaluator import evaluate
from observe import observe
from church import pred, num, true, false, pair
from demo import loop, fact, fib

class TargetTests(unittest.TestCase):
 def test_capture_avoidance(self):
  out=substitute(Lam("y",Var("x")),"x",Var("y")); self.assertNotEqual(out.name,"y"); self.assertEqual(free_vars(out),{"y"})
 def test_budget_and_weakness(self):
  i=Lam("x",Var("x")); self.assertTrue(evaluate_target(i,0).complete); self.assertFalse(evaluate_target(App(i,i),0).complete); self.assertTrue(evaluate_target(App(i,i),1).complete)
  self.assertEqual(evaluate_target(Lam("x",App(i,Var("x"))),0).steps,0)

class CompilerTests(unittest.TestCase):
 def check_compiled(self,e,k,answer):
  r=evaluate(compile_expr(e),500000); self.assertTrue(r.complete); self.assertEqual(observe(r.value,k,500000),answer)
 def test_arithmetic_and_comparisons(self):
  cases=[("+",2,3,5),("-",2,3,0),("*",2,3,6),("<",2,3,True),("<=",2,3,True),(">",2,3,False),(">=",2,2,True),("==",2,2,True),("!=",2,3,True)]
  for op, left, right, answer in cases:
   self.check_compiled(D0Eop2(op,D0Eint(left),D0Eint(right)),"bool" if isinstance(answer,bool) else "nat",answer)
 def test_control_pairs_and_scope(self):
  self.check_compiled(D0Eif0(D0Ebtf(True),D0Eint(1),D0Eint(9)),"nat",1)
  self.check_compiled(D0Eop2("and",D0Ebtf(False),D0Ebtf(True)),"bool",False)
  self.check_compiled(D0Eop2("or",D0Ebtf(True),D0Ebtf(False)),"bool",True)
  self.check_compiled(D0Epfst(D0Epair(D0Eint(2),D0Ebtf(True))),"nat",2)
  e=D0Elet("x",D0Eint(3),D0Eapp(D0Elam("y",D0Eop2("+",D0Evar("x"),D0Evar("y"))),D0Eint(4))); self.check_compiled(e,"nat",7)
 def test_open_and_rejections(self):
  self.assertEqual(free_vars(compile_expr(D0Eop2("+",D0Evar("s"),D0Evar("x")))), {"s", "x"})
  with self.assertRaises(CompileError): compile_expr(D0Eif0(D0Ebtf(True),D0Eint(0),D0Eint(-1)))
  with self.assertRaises(CompileError): compile_expr(D0Eop2("/",D0Eint(1),D0Eint(2)))
 def test_literals_boolean_not_nested_pair_and_fix(self):
  self.check_compiled(D0Eop1("not",D0Ebtf(False)), "bool", True)
  nested=D0Epair(D0Epair(D0Eint(2),D0Ebtf(True)), D0Eint(3))
  r=evaluate(compile_expr(nested),500000); self.assertEqual(observe(r.value,("pair",("pair","nat","bool"),"nat"),500000),((2,True),3))
  self.check_compiled(D0Eapp(D0Efix("f","f",D0Evar("f")),D0Eint(3)),"nat",3)
 def test_short_circuit_and_strict_positions(self):
  self.check_compiled(D0Eop2("and",D0Ebtf(False),loop()),"bool",False)
  self.check_compiled(D0Eop2("or",D0Ebtf(True),loop()),"bool",True)
  for e in [D0Elet("x",loop(),D0Eint(2)),D0Epfst(D0Epair(D0Eint(2),loop())),D0Epsnd(D0Epair(loop(),D0Ebtf(True))),D0Eapp(D0Elam("x",D0Eint(0)),loop())]:
   self.assertFalse(evaluate(compile_expr(e),200).complete)
 def test_recursion_and_source_agreement(self):
  for e, expected in [(fact(4),24),(fib(5),5)]:
   self.assertEqual(evaluate(e),expected)
   r=evaluate(compile_expr(e),500000); self.assertTrue(r.complete); self.assertEqual(observe(r.value,"nat",500000),expected)

class EncodingTests(unittest.TestCase):
 def test_zero_and_predecessor_zero(self):
  for term, expected in [(num(0),0),(App(pred(),num(0)),0),(App(pred(),num(3)),2)]:
   r=evaluate_target(term,100000); self.assertTrue(r.complete); self.assertEqual(observe(r.value,"nat",100000),expected)
 def test_library_closed_and_boolean_observation(self):
  for term in [num(0), num(4), true(), false(), pair(), pred()]: self.assertEqual(free_vars(term),set())
  self.assertEqual(observe(true(),"bool"),True); self.assertEqual(observe(false(),"bool"),False)

if __name__ == "__main__": unittest.main()
