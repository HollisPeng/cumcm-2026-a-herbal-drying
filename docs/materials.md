# Material provenance / 材料来源

## English

All project materials were supplied in the original workspace's `参考/` directory. No replacement data, new model, or new numerical result was introduced during repository preparation.

Except for the supplied third-party materials under `problem/`, the repository's original content is licensed under the root [MIT License](../LICENSE). The problem statement, attachments, and result templates retain their original rights status and are not relicensed under MIT.

| Supplied material | Repository location |
| --- | --- |
| `题目/A题/A题.pdf` | `problem/problem-A.pdf` |
| `题目/A题/附件/附件1.xlsx`, `附件2.xlsx` | `problem/attachments/` (original filenames) |
| `题目/A题/附件/附件3/result*.xlsx` | `problem/templates/` |
| `完成结果/A题_参赛论文.pdf`, `.docx` | `paper/herbal-drying.pdf`, `.docx` |
| `完成结果/A题_支撑材料/code/`, `data/`, `figures/`, `results/` | Corresponding top-level directories |
| `完成结果/A题_支撑材料/result*.xlsx` | `results/workbooks/` |
| `完成结果/A题_支撑材料/requirements.txt` | `requirements.txt` |

The paper PDF and Word source are preserved byte for byte under neutral filenames. The study was completed out of personal interest; the author did not participate in the 2026 contest, and the paper is not an official submission. Appendix A's references to an anonymous support ZIP describe the original packaging, not the status of this repository. Use the root README for current paths and commands: completed workbooks now reside in `results/workbooks/`. The Word source and reading PDF serve distinct purposes and are intentionally both retained.

The numerical solver, plot script, input CSVs, completed workbooks, saved results, and figures are unchanged. `verify.py` now locates the relocated workbooks, checks the Q4 radius sheet, and supports a read-only `--files-only` mode. `export_results.mjs` exports to the relocated workbook directory. The paper's code appendix is the original snapshot; these repository-maintenance changes do not alter the model.

Original attachment workbooks document data provenance; CSV transcriptions provide direct program inputs. Original blank templates document the specified output layout; completed workbooks contain the study's results. CSV outputs retain more precision than the reading workbooks. These formats are complementary, not redundant copies.

The old submission-oriented README was replaced by the bilingual project documentation. The competition-only `format2026.doc` was omitted because it does not contribute to understanding or reproducing the study. The original staging directory was removed after retained files were copied and SHA-256 checked.

## 中文

项目材料均来自原工作区的 `参考/` 文件夹。本次整理没有引入替代数据、新模型或新的数值成果。

除 `problem/` 下所提供的第三方材料外，本仓库的原创内容采用根目录中的 [MIT 许可证](../LICENSE)授权。题目、附件和结果模板保留其原有权利状态，不在 MIT 许可证的重新授权范围内。

| 原始材料 | 仓库位置 |
| --- | --- |
| `题目/A题/A题.pdf` | `problem/problem-A.pdf` |
| `题目/A题/附件/附件1.xlsx`、`附件2.xlsx` | `problem/attachments/`（保留原文件名） |
| `题目/A题/附件/附件3/result*.xlsx` | `problem/templates/` |
| `完成结果/A题_参赛论文.pdf`、`.docx` | `paper/herbal-drying.pdf`、`.docx` |
| `完成结果/A题_支撑材料/code/`、`data/`、`figures/`、`results/` | 对应的仓库顶层目录 |
| `完成结果/A题_支撑材料/result*.xlsx` | `results/workbooks/` |
| `完成结果/A题_支撑材料/requirements.txt` | `requirements.txt` |

论文 PDF 与 Word 源文件仅改用中性文件名，文件内容逐字节保留。作者出于个人兴趣完成研究，没有参加该届竞赛，论文不属于正式参赛作品。附录 A 中“匿名电子材料”“支撑材料压缩包”等措辞描述的是历史打包方式，不代表本仓库的作品性质。当前路径和命令以根目录 README 为准：已完成工作簿现位于 `results/workbooks/`。Word 编辑源文件和 PDF 阅读版各有用途，因此均予保留。

数值求解器、绘图脚本、输入 CSV、成品工作簿、已有数值结果及图表均未修改。`verify.py` 调整了工作簿路径，补充了问题四半径表核验，并增加只读的 `--files-only` 选项；`export_results.mjs` 的输出路径同步调整。论文代码附录保留原始快照，这些仓库维护修改不改变模型。

原始附件工作簿保留数据来源，CSV 转录便于程序直接读取；原始空白模板记录题目指定格式，成品工作簿承载研究结果；输出 CSV 比阅读用工作簿保留更高精度。它们用途互补，并非无意义的重复副本。

原提交导向 README 已替换为双语项目文档。仅服务于竞赛提交格式的 `format2026.doc` 不参与成果理解或复现，未予保留。保留材料完成复制及 SHA-256 校验后，原始暂存目录已清除。
