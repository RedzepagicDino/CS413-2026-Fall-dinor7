import unittest
from visitors import *

class VisitorTests(unittest.TestCase):
    def test_pretty_every_constructor(self):
        e=D0Eif0(D0Ebtf(True),D0Eapp(D0Elam('x',D0Eop1('+1',D0Evar('x'))),D0Eint(-999999999999)),D0Elet('z',D0Epair(D0Eint(1),D0Eint(2)),D0Eop2('+',D0Epfst(D0Evar('z')),D0Epsnd(D0Evar('z')))))
        self.assertEqual(d0exp_pretty(e),'(if true then ((lam x. (+1 x)) -999999999999) else (let z = (pair 1 2) in ((fst z) + (snd z))))')
        self.assertEqual(d0exp_pretty(D0Efix('f','n',D0Eop2('/',D0Eint(1),D0Eint(0)))),'(fix f(n). (1 / 0))')
        self.assertEqual(d0exp_pretty(D0Ebtf(False)),'false')
    def test_capture_and_shadowing(self):
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Elam('y',D0Eop2('+',D0Evar('x'),D0Evar('y'))),'x',D0Evar('y'))),'(lam y_1. (y + y_1))')
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Elet('x',D0Evar('x'),D0Evar('x')),'x',D0Eint(3))),'(let x = 3 in x)')
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Efix('f','n',D0Eapp(D0Evar('f'),D0Evar('x'))),'x',D0Epair(D0Evar('f'),D0Evar('n')))),'(fix f_1(n_2). (f_1 (pair f n)))')
        same=D0Efix('f','f',D0Evar('f')); self.assertEqual(d0exp_pretty(d0exp_substitute(same,'f',D0Eint(9))), '(fix f(f). f)')
    def test_free_variable_property_and_no_mutation(self):
        e=D0Elam('y',D0Eop2('+',D0Evar('x'),D0Evar('z'))); before=d0exp_pretty(e)
        got=d0exp_substitute(e,'x',D0Evar('y'))
        self.assertEqual(d0exp_fvset(got),{'y','z'}); self.assertEqual(d0exp_pretty(e),before)
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Evar('x'),'x',D0Eop2('+',D0Evar('x'),D0Eint(1)))),'(x + 1)')
        self.assertEqual(d0exp_pretty(d0exp_substitute(e,'q',D0Evar('y'))),before)

if __name__ == '__main__': unittest.main()
