import math
import unittest
from fractions import Fraction as F
from lab_calc import mean_a, percent_difference, fh, damping, halfwidth, linear_fit, format_result, run


class LabCalculationTests(unittest.TestCase):
    def test_mean_exact_reference(self):
        r=mean_a([1,2,3]); self.assertEqual(r['mean'],2); self.assertEqual(r['sum_squares'],2)
        self.assertAlmostEqual(r['u_a'],math.sqrt(1/3))
    def test_classroom_fraction_reference(self):
        p=[17,28.2,39.6,51.6,64,77]
        r=fh(p,11.6,'classroom_adjacent_about_successive')
        # Independent rational arithmetic expected values.
        self.assertAlmostEqual(r['mean'],float(F(539,45)))
        self.assertAlmostEqual(r['sum_squares'],float(F(4379,2025)))
        self.assertAlmostEqual(r['u_a'],math.sqrt(float(F(4379,40500))))
        self.assertAlmostEqual(r['signed_percent'],float(F(1700,522)))
    def test_alternate_method_distinct(self):
        r=fh([17,28.2,39.6,51.6,64,77],11.6,'successive_groups_mean_a')
        self.assertAlmostEqual(r['u_a'],math.sqrt(float(F(148,2025))))
        self.assertEqual(r['n'],3)
    def test_no_method_guess(self):
        with self.assertRaises(ValueError): fh([1,2,3,4,5,6],1,'auto')
    def test_missing_reference(self):
        with self.assertRaises(KeyError): run({'operation':'fh','unit':'V','peaks':[1,2,3,4,5,6],'method':'classroom_adjacent_about_successive'})
    def test_wrong_unit(self):
        with self.assertRaises(ValueError): run({'operation':'fh','unit':'mV'})
    def test_peak_order(self):
        with self.assertRaises(ValueError): fh([1,2,3,3,5,6],1,'classroom_adjacent_about_successive')
    def test_single_sample(self):
        with self.assertRaises(ValueError): mean_a([1])
    def test_nonfinite(self):
        for v in (float('nan'),float('inf'),True,'2',None):
            with self.subTest(v=v),self.assertRaises(ValueError): mean_a([1,v])
    def test_percent_sign(self):
        self.assertEqual(percent_difference(9,10,True),-10)
        self.assertEqual(percent_difference(9,10),10)
    def test_zero_reference(self):
        with self.assertRaises(ValueError): percent_difference(1,0)
    def test_exponential_damping(self):
        values=[100*math.exp(-.08*1.5*i) for i in range(10)]
        r=damping(values,1.5,5)
        self.assertAlmostEqual(r['mean'],.08,14); self.assertLess(r['u_a'],1e-15)
    def test_damping_invalid(self):
        for a,t,k in [([1,0,1,1],1,2),([1,2,3,4],0,2),([1,2,3],1,2)]:
            with self.subTest(a=a),self.assertRaises(ValueError): damping(a,t,k)
    def test_halfwidth(self):
        self.assertAlmostEqual(halfwidth(2,.9,1.1,True)['beta'],math.pi/10)
    def test_no_approximation_guess(self):
        with self.assertRaises(ValueError): halfwidth(2,.9,1.1,False)
    def test_fit_exact(self):
        r=linear_fit([0,1,2,3],[1,3,5,7])
        self.assertEqual(r['slope'],2); self.assertEqual(r['intercept'],1); self.assertEqual(r['r_squared'],1)
    def test_fit_constant_y(self):
        self.assertIsNone(linear_fit([0,1,2],[4,4,4])['r_squared'])
    def test_fit_degenerate(self):
        with self.assertRaises(ValueError): linear_fit([1,1,1],[1,2,3])
    def test_format_ordinary(self):
        r=format_result(11.977777,.32882)
        self.assertEqual((r['value_text'],r['uncertainty_text']),('11.98','0.33'))
    def test_format_carry(self):
        r=format_result(1.23456,.0996)
        self.assertEqual((r['value_text'],r['uncertainty_text']),('1.23','0.10'))
    def test_zero_uncertainty_no_precision_guess(self):
        with self.assertRaises(ValueError): format_result(1,0)


if __name__=='__main__': unittest.main(verbosity=2)
