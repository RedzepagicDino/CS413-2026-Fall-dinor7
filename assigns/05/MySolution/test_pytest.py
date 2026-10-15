from visitors import *

def test_all_remaining_forms_and_nonmatching_variable():
    e=D0Eop2('*',D0Eop1('-1',D0Evar('x')),D0Eapp(D0Evar('g'),D0Evar('x')))
    assert d0exp_pretty(d0exp_substitute(e,'x',D0Eint(4))) == '((-1 4) * (g 4))'
    assert d0exp_pretty(d0exp_substitute(e,'q',D0Eint(4))) == d0exp_pretty(e)

def test_let_initializer_and_fresh_collision_are_distinct():
    e=D0Elet('y',D0Evar('x'),D0Elam('y_1',D0Eop2('+',D0Evar('x'),D0Evar('y'))))
    got=d0exp_substitute(e,'x',D0Evar('y'))
    assert d0exp_pretty(got) == '(let y_2 = y in (lam y_1. (y + y_2)))'
    assert d0exp_pretty(d0exp_substitute(e,'x',D0Evar('y'))) == d0exp_pretty(got)

def test_fix_binder_capture_and_inputs_unchanged():
    e=D0Efix('f','n',D0Eop2('+',D0Evar('x'),D0Eapp(D0Evar('f'),D0Evar('n')))); r=D0Evar('f')
    assert d0exp_pretty(d0exp_substitute(e,'x',r)) == '(fix f_1(n). (f + (f_1 n)))'
    assert d0exp_pretty(e) == '(fix f(n). (x + (f n)))'

def test_substitution_visits_literals_conditionals_pairs_and_projections():
    e = D0Eif0(D0Evar('x'), D0Epair(D0Epfst(D0Evar('x')), D0Epsnd(D0Evar('x'))), D0Ebtf(False))
    assert d0exp_pretty(d0exp_substitute(e, 'x', D0Epair(D0Eint(7), D0Eint(8)))) == '(if (pair 7 8) then (pair (fst (pair 7 8)) (snd (pair 7 8))) else false)'
    assert d0exp_pretty(d0exp_substitute(D0Eint(2), 'x', D0Eint(9))) == '2'
    assert d0exp_pretty(d0exp_substitute(D0Ebtf(True), 'x', D0Eint(9))) == 'true'

def test_nested_shadowing_is_not_renamed_as_an_outer_binding():
    e = D0Elam('y', D0Epair(D0Evar('x'), D0Elam('y', D0Eop2('+', D0Evar('x'), D0Evar('y')))))
    assert d0exp_pretty(d0exp_substitute(e, 'x', D0Evar('y'))) == '(lam y_1. (pair y (lam y_2. (y + y_2))))'
