# 药材烘干 — 2026 全国大学生数学建模竞赛 A 题

[English](README.md) | [简体中文](README.zh-CN.md)

本项目基于 **2026 年全国大学生数学建模竞赛（CUMCM）A 题**，研究圆柱形药材烘干过程中的传热与水分输运，汇集已完成的论文、源代码、题目数据、数值结果及图表。

**作者出于个人兴趣完成该题，没有参加 2026 年该届竞赛，本项目不属于正式参赛作品。** 项目完成过程中使用了 **GPT-5.6 Sol** 和 **GPT-6 Astra** 的协助。

## 阅读入口

- 阅读[论文 PDF（中文）](paper/herbal-drying.pdf)；[Word 源文件](paper/herbal-drying.docx)用于后续编辑。
- 查阅[完整原始题目](problem/problem-A.pdf)。
- 浏览[结果工作簿](results/workbooks)、[数值汇总](results/summary.json)和[图表](figures)。
- [材料来源与保留说明](docs/materials.md)介绍原始文件的对应关系及论文附录历史路径的解释。

## 项目背景与方法

题目研究长 25 cm、初始半径 2 cm 的圆柱形药材，初始温度均为 28 °C，干基含水率均为 2.55 kg/kg。四问分别涉及预热、变物性烘干、固定半径下的干燥终点，以及考虑实测收缩的烘干过程。

现有成果采用轴对称径向传热传质模型、表面加密有限体积法、积分形式的水分扩散势以及 SciPy 隐式 BDF 时间积分。问题二、三共用从初始状态出发的同一条变物性轨迹。问题四结合移动物质坐标、实测半径及该问指定的物性公式。

## 已有成果

以下数值来自保留的论文和 [summary.json](results/summary.json)，本次仓库整理未重新计算模型。

| 问题 | 已有结果 |
| --- | --- |
| 问题一：预热 1,800 s | 中心 / 表面温度：**33.5753 / 36.7856 °C**；含水率：**2.5500 / 1.5102 kg/kg** |
| 问题二：前三小时 | 中心 / 表面温度：**49.8495 / 49.9664 °C**；含水率：**1.7662 / 1.0081 kg/kg** |
| 问题三：固定半径 | 临界时长：**57.4723 h**；首个严格达标整秒：**206,901 s（57.4725 h）** |
| 问题四：实测收缩 | 临界时长：**51.0906 h**；首个严格达标整秒：**183,927 s（51.0908 h）** |

![已有固定半径与实测收缩模型的中心、表面含水率曲线](figures/04_drying.png)

终点使用**未舍入的空间最大含水率**判定。临界时刻对应 0.15 kg/kg，保存的结束行取首次严格低于该阈值的整秒。因此，显示为 `0.1500` 的数值仍可能满足停机条件。问题三、四同时改变物性和几何条件，其时长差不能全部归因于收缩。

已有记录包含 N = 400、800、1,600 的网格对比、敏感性分析、水分平衡检查及常物性传热解析解对照。这些属于数值一致性检验，不是基于药材内部实测数据的实验验证。

## 仓库结构

```text
.
├── README.md                 英文说明
├── README.zh-CN.md           中文说明
├── LICENSE                   原创项目内容的 MIT 许可证
├── requirements.txt          Python 依赖
├── problem/
│   ├── problem-A.pdf         完整原始题目
│   ├── attachments/          原始附件 1、2 工作簿
│   └── templates/            原始四份结果模板
├── paper/
│   ├── herbal-drying.pdf     已完成论文阅读版
│   └── herbal-drying.docx    可编辑论文源文件
├── code/
│   ├── solve.py              原有数值模型与分析
│   ├── plot_results.py       五幅论文图的生成程序
│   ├── verify.py             文件核验与解析解对照
│   └── export_results.mjs    可选工作簿排版与导出
├── data/                     模型使用的 CSV 转录数据
├── results/
│   ├── workbooks/            已完成 result1.xlsx–result4.xlsx
│   ├── result*_T.csv         温度输出
│   ├── result*_C.csv         含水率输出
│   ├── radius_output.csv     问题四各输出时刻的表面半径
│   ├── summary.json          已有结果与数值分析
│   └── verification.json     原始核验记录
├── figures/                  五幅已有论文图
└── docs/
    └── materials.md          材料来源与保留说明
```

## 数据与输出约定

`data/air.csv` 转录附件 1：共 241 个时点，间隔 60 s，覆盖 0–14,400 s。`data/radius.csv` 转录附件 2：共 145 个时点，间隔 1,800 s，覆盖 0–72 h。原始 XLSX 保留在 `problem/attachments/`，便于核对。

| 工作簿 | 内容与采样 |
| --- | --- |
| [result1.xlsx](results/workbooks/result1.xlsx) | 温度、水分浓度两表；1–1,800 s，间隔 1 s；半径 0–2 cm，间隔 0.1 cm |
| [result2.xlsx](results/workbooks/result2.xlsx) | 温度、水分浓度两表；1–10,800 s，间隔 1 s；径向坐标同上 |
| [result3.xlsx](results/workbooks/result3.xlsx) | 从 60 s 起每隔 60 s 的含水率，补入终点；共 3,449 行；半径 0–2 cm |
| [result4.xlsx](results/workbooks/result4.xlsx) | 从 60 s 起每隔 60 s 的含水率，补入终点；共 3,066 行；固定半径 0–1.9 cm 加实际移动表面；第二工作表记录表面半径 |

时间单位为秒，CSV 径向表头单位为厘米，温度单位为 °C，含水率单位为干基 kg/kg。模型内部使用米，Arrhenius 公式内的温度转换为开尔文。初始条件在代码中给定，输出表从首个正采样时刻开始。

工作簿保存四位小数的静态数值，对应 CSV 保存四位小数舍入前约十位有效数字。问题四中的空白单元格、CSV `nan` 和 JSON `null` 表示坐标位于收缩后的药材外部，**不表示零**。固定 2 cm 坐标在所有保存时刻均处于域外，因此问题四省略该列；末列始终代表实际表面。

## 使用说明

### 阅读与检查已有结果

阅读论文、图表和工作簿无需运行计算。使用 Python 工具时，采用 Python 3.12，在仓库根目录安装依赖：

```bash
python -m venv .venv
# 激活：Windows PowerShell：.venv\Scripts\Activate.ps1
# 激活：macOS/Linux：source .venv/bin/activate
python -m pip install -r requirements.txt
python code/verify.py --files-only
```

`--files-only` 对照已有 CSV 检查六张温度 / 含水率结果表及问题四半径表，涵盖尺寸、时间、空白位置和舍入误差。该选项不执行数值求解，也不覆盖原始核验记录。

### 复现原有计算（可选）

以下命令供希望重新生成已有成果的读者使用。**命令会覆盖数值结果和图表**；如需保留仓库中的原始成果，请在单独副本中运行。

```bash
python code/solve.py --n 800 --validation
python code/plot_results.py
python code/verify.py
```

原始材料记录的环境为 Python 3.12 / SciPy 1.17.0，N = 800，相对容差 `2e-8`，绝对容差 `2e-10`。`requirements.txt` 保留原有最低兼容版本约束，并非完整锁定环境；依赖版本差异可能产生小幅数值变化。

求解器不使用随机数，依赖安装后无需网络。求解会生成绘图所需的三份 `results/*_profiles.npz`，这些可重建中间文件已被 Git 忽略，五幅成品图则随仓库保留。在全新副本中单独运行绘图脚本前，需要先生成 NPZ。省略 `--validation` 只重建主结果，新写入的汇总文件将不再包含收敛和敏感性分析。默认运行 `verify.py` 还会进行解析传热测试并覆盖 `results/verification.json`，不会修改 XLSX 文件。

### 可选工作簿导出

原有 `export_results.mjs` 用于已求得 CSV 的排版。按原始材料说明，它要求 Node.js 环境能解析 2.8.58 或以上版本的 `@oai/artifact-tool`；这是独立于 Python 依赖的可选 Codex 专用依赖。

```bash
node code/export_results.mjs 1
node code/export_results.mjs 2
node code/export_results.mjs 3
node code/export_results.mjs 4
```

导出会覆盖 `results/workbooks/result*.xlsx`，并在被忽略的 `previews/` 中生成预览。没有该依赖时，仍可阅读已有工作簿、运行全部 Python 计算并核验 CSV。

## 假设与局限

烘房条件在前四小时观测区间内采用线性插值，此后保持 **50 °C、0.05 kg/kg**。这一延拓是模型假设，不是实测记录。半径也采用线性插值，已有问题四终点位于 72 h 观测区间内。

模型采用径向对称、等效水分边界及均匀骨架收缩假设，忽略轴向输运、辐射及潜热耦合，经验密度仅参与热容计算。结果应在这些假设下理解；附件不含独立的药材内部温度或含水率观测，无法据此开展实验验证。

## 来源与使用许可

除 `problem/` 下的第三方材料外，本仓库的原创内容采用 [MIT 许可证](LICENSE)授权。

题目、输入附件和结果模板来自所提供的 2026 年全国大学生数学建模竞赛 A 题材料，仍受各自权利人的权利约束，不在 MIT 许可证的重新授权范围内。收录这些材料不表示与竞赛主办方存在隶属关系或获得其认可，详见[材料说明](docs/materials.md)。
