#!/usr/bin/env python3
"""Small, explicit lab calculations. No inferred model, units, data, or rounding."""
import argparse
import json
import math
from decimal import Decimal, ROUND_HALF_UP


def numbers(values, minimum=2):
    if not isinstance(values, (list, tuple)) or len(values) < minimum:
        raise ValueError(f'至少需要{minimum}个数值')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError('输入必须是有限数值，不能有缺失值、布尔值或非数')
    return [float(x) for x in values]


def positive(value):
    value = numbers([value], 1)[0]
    if value <= 0:
        raise ValueError('参数必须大于0')
    return value


def mean_a(values):
    values = numbers(values)
    n = len(values)
    avg = math.fsum(values) / n
    ss = math.fsum((v - avg)**2 for v in values)
    return {'n': n, 'mean': avg, 'sum_squares': ss,
            'u_a': math.sqrt(ss / (n * (n - 1))),
            'formula': 'sqrt(sum((x_i-mean)^2)/(n*(n-1)))',
            'assumption': '适用于独立同分布重复量的均值；需另核相关性与系统影响'}


def percent_difference(value, reference, signed=False):
    value, reference = numbers([value, reference])
    if reference == 0:
        raise ValueError('参考值不能为0')
    # Signed relative deviation uses the signed reference definition explicitly.
    delta = (value-reference)/reference*100
    return delta if signed else abs(delta)


def fh(peaks, reference, method):
    peaks = numbers(peaks, 6)
    if len(peaks) != 6 or any(b <= a for a, b in zip(peaks, peaks[1:])):
        raise ValueError('此模型要求恰好6个严格递增峰电压，单位V')
    positive(reference)
    differences = [b-a for a, b in zip(peaks, peaks[1:])]
    groups = [(peaks[i+3]-peaks[i])/3 for i in range(3)]
    group_mean = math.fsum(groups)/3
    if method == 'classroom_adjacent_about_successive':
        center = group_mean
        samples = differences
        note = '课堂指定口径；不解释为已处理共享峰位相关性的通用标准误'
    elif method == 'successive_groups_mean_a':
        center = group_mean
        samples = groups
        note = '三组逐差重复量，需核独立性假设；不能覆盖其他课堂指定方法'
    else:
        raise ValueError('必须明确选择已支持的方法，禁止默认套用')
    n = len(samples)
    ss = math.fsum((v-center)**2 for v in samples)
    return {'method': method, 'unit': 'V', 'mean': center,
            'successive_groups': groups, 'adjacent_differences': differences,
            'uncertainty_samples': samples, 'n': n, 'sum_squares': ss,
            'sum_squares_unit': 'V^2', 'u_a': math.sqrt(ss/(n*(n-1))),
            'reference': reference, 'signed_percent': percent_difference(center, reference, True),
            'formula': 'sqrt(sum((sample_i-center)^2)/(n*(n-1)))', 'note': note}


def damping(amplitudes, period_s, lag):
    amplitudes = numbers(amplitudes)
    period_s = positive(period_s)
    if type(lag) is not int or lag < 1 or len(amplitudes) != 2*lag:
        raise ValueError('此配对法要求恰好2k个连续峰幅值，lag=k正整数')
    if any(x <= 0 for x in amplitudes):
        raise ValueError('峰幅值必须大于0，不能直接输入带符号极小值')
    betas = [math.log(amplitudes[i]/amplitudes[i+lag])/(lag*period_s) for i in range(lag)]
    if lag < 2:
        raise ValueError('A类估计至少需要两对峰值')
    result = mean_a(betas)
    result.update({'betas': betas, 'unit': 's^-1', 'period_s': period_s,
                   'lag': lag, 'warning': '出现负β或单调趋势时核模型与原记录，不删除数据'})
    return result


def halfwidth(t0_s, r1, r2, weak_damping):
    t0_s, r1, r2 = positive(t0_s), positive(r1), positive(r2)
    if weak_damping is not True or r2 <= r1:
        raise ValueError('必须明确确认弱阻尼近似且r2>r1')
    return {'beta': math.pi*(r2-r1)/t0_s, 'unit': 's^-1',
            'formula': 'beta ≈ pi*(r2-r1)/T0', 'approximation': 'weak damping'}


def linear_fit(x, y):
    x, y = numbers(x, 3), numbers(y, 3)
    if len(x) != len(y):
        raise ValueError('x与y长度不同')
    xm, ym = math.fsum(x)/len(x), math.fsum(y)/len(y)
    sxx = math.fsum((v-xm)**2 for v in x)
    if sxx == 0:
        raise ValueError('x没有变化，不能线性拟合')
    slope = math.fsum((a-xm)*(b-ym) for a,b in zip(x,y))/sxx
    intercept = ym-slope*xm
    residuals = [b-(slope*a+intercept) for a,b in zip(x,y)]
    sse = math.fsum(r*r for r in residuals)
    syy = math.fsum((v-ym)**2 for v in y)
    return {'slope': slope, 'intercept': intercept, 'residuals': residuals,
            'r_squared': None if syy == 0 else 1-sse/syy,
            'slope_standard_error': math.sqrt(sse/(len(x)-2)/sxx),
            'assumption': '含截距的未加权OLS；x误差忽略，y独立等方差，单位由输入量推导'}


def format_result(value, uncertainty, significant_digits=2):
    value, uncertainty = numbers([value, uncertainty])
    if uncertainty <= 0 or type(significant_digits) is not int or significant_digits not in (1,2):
        raise ValueError('需正不确定度及1或2位有效数字；零不确定度不得自动推断精度')
    u = Decimal(str(uncertainty))
    q = Decimal(1).scaleb(u.adjusted()-significant_digits+1)
    rounded = u.quantize(q, rounding=ROUND_HALF_UP)
    # Recompute position after rounding across a power of ten, e.g. 0.0996 -> 0.10.
    q = Decimal(1).scaleb(rounded.adjusted()-significant_digits+1)
    rounded = rounded.quantize(q, rounding=ROUND_HALF_UP)
    v = Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP)
    return {'value_text': format(v, 'f'), 'uncertainty_text': format(rounded, 'f'),
            'rounding': 'decimal ROUND_HALF_UP; classroom rules may override'}


def run(data):
    operation = data['operation']
    if operation == 'fh':
        if data.get('unit') != 'V':
            raise ValueError('fh输入单位必须显式为V，请先换算')
        return fh(data['peaks'], data['reference'], data['method'])
    if operation == 'mean_a': return mean_a(data['values'])
    if operation == 'damping': return damping(data['amplitudes'], data['period_s'], data['lag'])
    if operation == 'halfwidth': return halfwidth(data['t0_s'], data['r1'], data['r2'], data['weak_damping'])
    if operation == 'linear_fit': return linear_fit(data['x'], data['y'])
    if operation == 'format_result': return format_result(data['value'], data['uncertainty'], data.get('significant_digits', 2))
    raise ValueError('未知operation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_json', help='UTF-8 JSON input path')
    args = parser.parse_args()
    try:
        with open(args.input_json, encoding='utf-8') as f:
            result = run(json.load(f))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'输入/模型错误: {exc}\n')
