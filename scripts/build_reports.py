"""Render dated Chinese reports from checked-in evidence and editorial choices."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERIOD_ZH = {'daily': '日榜', 'weekly': '周榜', 'monthly': '月榜'}


def load(name: str) -> dict:
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8-sig'))


def main() -> None:
    selected = load('directions.json')
    repo_evidence = load('repository_evidence.json')
    trend = load('trending_snapshot.json')
    posts = load('post_evidence.json')
    repos = {item['repository']: item for item in repo_evidence['repositories']}
    captured = {(row['repository'], snap['period']): row
                for snap in trend['snapshots'] for row in snap['repositories']}
    report = [
        '# GitHub 十大热门方向｜2026-10-09 采样版', '',
        '这是一份从当天 GitHub Trending 日、周、月榜样本归纳的**十个关注方向**。编号方便阅读，'
        '不表示热度顺序，也不是 GitHub 官方方向排名。分类有交叉；当前样本偏向 AI，'
        '不能据此推断全行业市场规模或哪个方向一定能获得 Stars。', '',
        '采样共包含 44 个榜单条目（不同时间窗可能重复），并通过官方仓库 API 核验 '
        '16 个代表项目。详情见[采样方法](采样方法与证据.md)和[data 原始证据](../data/)。', '',
        '累计 Stars 取自仓库 API；近期增星取自榜单所标注时间窗。抓取时刻略有差异，'
        '日、周、月的数字不能直接横向排名。', '',
        '| 方向 | 代表项目 | 累计 Stars | 榜单标注增星 |',
        '|---|---|---:|---:|'
    ]
    for choice in selected['directions']:
        name = choice['repository']
        metadata = repos[name]
        row = captured[name, choice['period']]
        report.append(f"| {choice['id']}. {choice['title']} | [{name}]({metadata['repository_url']}) | "
                      f"{metadata['cumulative_stars']:,} | {PERIOD_ZH[choice['period']]} +{row['period_stars']:,} |")
    report += ['', '**阅读方式：**先看读者的实际问题，再挑自己能做出完整示例的一小块。'
               '这里的项目想法属于编辑建议，未做商业需求或产品效果验证。']
    for choice in selected['directions']:
        metadata = repos[choice['repository']]
        row = captured[choice['repository'], choice['period']]
        report += ['', f"## {choice['id']}. {choice['title']}", '',
                   f"**读者要解决什么：**{choice['need']}", '',
                   f"**可做的小项目：**{choice['small_project']}", '',
                   f"**第一份演示：**{choice['demo']}", '',
                   f"**介绍怎么写：**{choice['content']}", '',
                   f"**要讲清的限制：**{choice['limit']}", '',
                   f"参考 [{choice['repository']}]({metadata['repository_url']})；"
                   f"[API 核验]({metadata['source_url']})时间 `{metadata['fetched_at_utc']}`；"
                   f"[{PERIOD_ZH[choice['period']]}来源]({row['source_url']})时间 `{row['fetched_at_utc']}`。"]
    report += ['', '## 个人开发者还可以关注什么', '',
               '当前周榜中，[text-to-cad](https://github.com/earthtojake/text-to-cad) 与 '
               '[openGym](https://github.com/DuarteSantos8/openGym) 也分别代表专业工程工具和个人自托管工具。'
               '它们提醒我们：解决一个具体问题的小工具，同样值得做，不必复制大型平台。', '',
               '高互动帖中的硬件改造、交互教学和科研文档工具属于跨方向补充；它们的历史积分'
               '不是当天 Trending 增长，见[高赞帖内容拆解](高赞帖内容拆解.md)。', '',
               '## 对现有 Origin / RC 项目的启发', '',
               '- Origin 项目最贴近“专业 Skill＋可编辑视觉”：先展示 OPJU、矢量图和可编辑 PPT，'
               '再解释软件要求与最短操作流程。',
               '- RC 项目适合突出“有出处的数据＋可复现的计算流程”：展示真实的运行输入、'
               '输出、训练测试分离及模型适用范围。',
               '- 给科研读者的价值是文件可用、计算可复现、方法可检查。'
               '主页改进本身不证明准确率提高，也不证明 Stars 已增长。', '']
    (ROOT / 'docs' / '十大热门方向.md').write_text('\n'.join(report), encoding='utf-8')

    breakdown = [
        '# 高赞技术帖究竟做了什么', '',
        '本页拆解 11 篇 2026 年 Show HN 发布帖。这里的“高赞”指帖子积分达到 100 以上的'
        '目的性样本，包含较早参考与 9 月近期参考；不是随机样本或年度排名。'
        '积分、评论数于 2026-10-09 从 HN 官方 API 核验，**都不是 GitHub Stars**。', '',
        '| 案例 | 发布日期（UTC） | HN 积分 | 评论数 | 做的方向 |',
        '|---|---|---:|---:|---|'
    ]
    for item in posts['posts']:
        breakdown.append(f"| [案例 {item['id']}]({item['post_url']}) | {item['published_at_utc'][:10]} | "
                         f"{item['points']:,} | {item['comments']:,} | {item['direction']} |")
    breakdown += ['', '## 一篇一篇看：内容、展示与反馈', '',
                  '以下描述总结作者介绍与讨论。项目性能、成本及隐私承诺属于作者报告，'
                  '本调研未独立运行这些项目；互动指标只说明讨论规模。']
    labels = ['HN.watch：熟悉内容转解释视频', 'ESP32：真实旧硬件改造', 'GPU 游戏：把原理变成互动',
              'ChartGPU：用可体验演示说明绘图能力', 'Micasa：解决自己的房屋管理问题',
              'Sweep：研究成果提供权重与集成入口', 'Dirac：公开实现与评测条件',
              'whichllm：帮助读者做具体硬件决策', 'Pdfwithlove：直接完成本地文件任务',
              'Agent Vault：围绕明确风险设计工具', 'TeXbrain：科研文档的可用工作流']
    for label, item in zip(labels, posts['posts']):
        breakdown += ['', f'### {label}', '',
                      f"**做了什么：**{item['content_summary_zh']}", '',
                      f"**展示方式：**{item['presentation_observation_zh']}", '',
                      f"**反馈与局限：**{item['constructive_critique_zh']}", '',
                      f"**可尝试借鉴：**{item['transferable_hypothesis_zh']}", '',
                      f"[原帖与讨论]({item['post_url']}) · [官方积分数据]({item['item_api_url']})"]
    breakdown += ['', '## 可以迁移到自己项目的内容结构', '',
                  '这些案例常出现以下顺序。它是整理材料的参考，不是经过实验验证的增星公式：', '',
                  '1. 具体问题：哪类读者遇到什么障碍。',
                  '2. 实际结果：给真实输出，而不是泛泛说“强大、领先”。',
                  '3. 体验入口：演示、最小样例、可以继续编辑的文件。',
                  '4. 最小使用步骤：依赖、输入、命令、输出。',
                  '5. 技术依据：版本、设置、可检查结果和已知限制。',
                  '6. 反馈入口：请读者描述自己的使用问题，Star 邀请保持简短和自愿。', '',
                  '## 平台适配', '',
                  'GitHub 首页和中文教程可以使用上述结构。技术社区应根据实际读者与现行规则准备材料。'
                  'HN 当前[规则](https://news.ycombinator.com/newsguidelines.html)禁止生成或 AI 编辑文本、'
                  '自动发帖与拉票；Skill 只整理事实和核对材料，由作者自己撰写最终 HN 文本。'
                  '[Show HN](https://news.ycombinator.com/showhn.html)面向可以体验的实际项目，'
                  '纯“十大方向”文章或清单不适合作为 Show HN。', '',
                  '完整字段、批评来源及抓取日期保存在[post_evidence.json](../data/post_evidence.json)。', '']
    (ROOT / 'docs' / '高赞帖内容拆解.md').write_text('\n'.join(breakdown), encoding='utf-8')
    print('Rendered two reports from checked-in evidence; no network requests or posting.')


if __name__ == '__main__':
    main()
