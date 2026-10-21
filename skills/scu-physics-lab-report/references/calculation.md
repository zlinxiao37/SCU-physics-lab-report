# 计算工具
使用Python标准库，无网络或额外依赖。命令：`python scripts/lab_calc.py /absolute/path/input.json`。
输入只用已核实当前数据，必须先匹配公式；输出保留精度，不是最终报告文本。公式出处和适用性仍需人工/模型判断。

## 支持的输入
```
{"operation":"fh","unit":"V","peaks":[17,28.2,39.6,51.6,64,77],"reference":11.6,"method":"classroom_adjacent_about_successive"}
{"operation":"mean_a","values":[1,2,3]}
{"operation":"damping","amplitudes":[100,90,80,70,60,50],"period_s":1.5,"lag":3}
{"operation":"halfwidth","t0_s":1.5115,"r1":0.9821,"r2":1.0187,"weak_damping":true}
{"operation":"linear_fit","x":[0,1,2,3],"y":[1,3,5,7]}
{"operation":"format_result","value":11.9777777778,"uncertainty":0.32882,"significant_digits":2}
```
示例数据仅用于演示，绝不移入新报告。
FH另一方法`successive_groups_mean_a`用于明确指定三组逐差统计的任务，不能自动替换课堂方法。
mean_a假设独立同分布重复量；不自动处理协方差。damping只支持2k个连续正峰值的k间隔配对，需至少2对。
halfwidth强制显式确认弱阻尼；非弱阻尼采用相应理论模型另算。
linear_fit仅含截距未加权OLS，x误差忽略、y独立等方差；斜率单位y/x、截距单位y。不要把R²高等同理论成立。
format_result采用十进制四舍五入，处理进位后末位对齐；老师规定其他修约方法时不用此格式函数。计算仍用未修约值。
单位换算、百分差定义、输入来源由调用者明确核对，工具不做OCR、不验证报告全体单位、不判断评分。
运行 `python scripts/test_lab_calc.py` 验证已支持数值行为，不能把通过率当现实报告准确率。
