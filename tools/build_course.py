"""Build a self-contained lesson from the existing Markdown (no browser dependencies)."""
import base64
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]

SHORT_TITLES = ['认识物质', '原子、元素与粒子', '化学键与结构', '状态、溶解与混合', '反应与质量守恒', '摩尔与浓度', '能量与反应速度', '动态平衡', '酸和碱', '氧化还原']
SUMMARIES = [
    '从一只玻璃杯开始，分清“看起来是什么”和“实际由什么组成”。',
    '四个常见名词，分别回答四个不同的问题。',
    '成分相同，连接和排列不同，性质也可能大不一样。',
    '看不见，不代表不存在；溶得快，也不代表能溶得更多。',
    '连接方式改变了，原子的种类和数量仍然对得上。',
    '不为计算而计算，只为把“多少”说清楚。',
    '能不能发生、发生得多快、效果好不好，要分开讨论。',
    '宏观上没有变化，微观过程却可能一直在继续。',
    '理解酸碱性，也理解一个指标能说明什么、不能说明什么。',
    '在生锈与电池之间，找到电子转移这条共同线索。',
]


def render_markdown(text):
    # Python-Markdown requires a blank line before a list after a paragraph.
    lines = text.splitlines()
    normalized = []
    for line in lines:
        if re.match(r'^[-*] ', line) and normalized and normalized[-1].strip() and not re.match(r'^[-*] ', normalized[-1]):
            normalized.append('')
        normalized.append(line)
    output = markdown.markdown('\n'.join(normalized), extensions=['tables', 'sane_lists'])
    output = re.sub(r'<a href="(https://[^"]+)"', r'<a class="source-link" target="_blank" rel="noopener noreferrer" href="\1"', output)
    output = output.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    output = output.replace('<hr />', '')
    for formula in ['2H₂ + O₂ → 2H₂O', '10 克 ÷ 100 克 = 10%']:
        output = output.replace(f'<p><strong>{formula}</strong></p>', f'<p class="formula"><strong>{formula}</strong></p>')
    output = re.sub(r'(<h3>必须记住的安全边界</h3>)(.*)$', r'<aside class="safety-note">\1\2</aside>', output, flags=re.S)
    output = re.sub(r'(<p><strong>两项观察都不品尝试验液.*?</p>)', r'<aside class="safety-note">\1</aside>', output, flags=re.S)
    return output.strip()


def adapt_scope(text):
    """Only adapt lesson-level wording; preserve the original Markdown download."""
    return text.replace('每次读一两讲', '每次读一两个小节').replace('这一讲', '这一节').replace('第三讲', '第 3 小节')


def states_figure():
    groups = []
    positions = [
        [(44 + c * 20, 63 + r * 20) for r in range(3) for c in range(4)],
        [(29, 109), (49, 105), (70, 109), (91, 106), (114, 109), (39, 86), (61, 89), (84, 85), (106, 88), (55, 67), (78, 66), (99, 66)],
        [(22, 36), (65, 23), (124, 34), (47, 64), (94, 53), (132, 79), (24, 95), (72, 97), (107, 119), (145, 119), (41, 125), (143, 19)],
    ]
    labels = [('固体', '相对固定的位置'), ('液体', '相邻但可以流动'), ('气体', '分散在更大空间')]
    for index, dots in enumerate(positions):
        circles = ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#4e735b"/>' for x, y in dots)
        groups.append(f'<g transform="translate({index * 196 + 8},0)"><rect x="0" y="0" width="172" height="147" rx="3" fill="#f9f8f0" stroke="#ccd3c0"/>{circles}<text x="86" y="173" text-anchor="middle" font-size="16" fill="#294b3b">{labels[index][0]}</text><text x="86" y="195" text-anchor="middle" font-size="12" fill="#66715f">{labels[index][1]}</text></g>')
    return '<figure class="inline-figure"><span class="figure-label">把镜头拉近 / 物质的三种状态</span><svg viewBox="0 0 584 204" role="img" aria-labelledby="states-title"><title id="states-title">固体、液体和气体中粒子排列的简化对比，固体粒子并非静止不动</title>' + ''.join(groups) + '</svg><figcaption>每幅图都画了 12 个粒子。位置与间距只帮助理解，不代表真实比例或运动轨迹；固体粒子也在振动。</figcaption></figure>'


def conservation_figure():
    return '''<figure class="inline-figure"><span class="figure-label">不是咒语，是一本粒子账本</span>
<svg viewBox="0 0 590 144" role="img" aria-labelledby="balance-title"><title id="balance-title">两个氢分子加一个氧分子生成两个水分子，两侧都是四个氢原子和两个氧原子</title>
<rect x="5" y="8" width="244" height="121" rx="3" fill="#f9f8f0" stroke="#ccd3c0"/><rect x="340" y="8" width="244" height="121" rx="3" fill="#f9f8f0" stroke="#ccd3c0"/>
<text x="127" y="39" text-anchor="middle" font-size="12" fill="#65705e">反应前</text><text x="462" y="39" text-anchor="middle" font-size="12" fill="#65705e">反应后</text>
<text x="127" y="77" text-anchor="middle" font-size="28" fill="#254b3c">2H₂ + O₂</text><text x="462" y="77" text-anchor="middle" font-size="28" fill="#254b3c">2H₂O</text>
<text x="127" y="109" text-anchor="middle" font-size="13" fill="#8d4633">4 个 H · 2 个 O</text><text x="462" y="109" text-anchor="middle" font-size="13" fill="#8d4633">4 个 H · 2 个 O</text>
<path d="M273 68h42l-8-7m8 7-8 7" fill="none" stroke="#617b56" stroke-width="2"/></svg>
<figcaption>变的是组合方式，不变的是每种原子的数量。这里只读懂模型，不进行氢气或点火实验。</figcaption></figure>'''


def energy_figure():
    return '''<figure class="inline-figure"><span class="figure-label">反应示意 / 换一条更容易走的路</span>
<svg viewBox="0 0 590 257" role="img" aria-labelledby="energy-title"><title id="energy-title">催化与未催化反应能量示意。两条路径有相同的起点和终点，催化路径的能垒较低</title>
<path d="M54 22v196h488" fill="none" stroke="#939e88" stroke-width="1.2"/>
<text x="14" y="28" font-size="12" fill="#66735e">能量</text><text x="476" y="246" font-size="12" fill="#66735e">反应进程 →</text>
<path d="M68 143h46C173 143 185 39 267 39S348 190 432 190h81" fill="none" stroke="#a6533d" stroke-width="3"/>
<path d="M68 143h46C175 143 196 96 265 96S347 190 432 190h81" fill="none" stroke="#426b4e" stroke-width="3" stroke-dasharray="7 4"/>
<text x="333" y="48" font-size="13" fill="#9b4732">未催化路径</text><text x="287" y="109" font-size="13" fill="#315d40">催化路径</text>
<text x="69" y="166" font-size="12" fill="#596852">反应物</text><text x="463" y="181" font-size="12" fill="#596852">产物</text>
<circle cx="69" cy="143" r="4" fill="#33543d"/><circle cx="512" cy="190" r="4" fill="#33543d"/>
</svg><figcaption>以一个放热反应作定性示意：催化路径的能垒较低，起点和终点不变。曲线不是实测数据，横轴也不是时间。</figcaption></figure>'''


def build():
    source = (ROOT / '化学入门教程.md').read_text(encoding='utf-8')
    pattern = r'(?m)^(## 第[一二三四五六七八九十]+讲：[^\n]+|# 两个不需要化学试剂的小观察|# 怎样知道自己真的开始理解了？|# 学完这些基础，下一步学什么？)\s*$'
    matches = list(re.finditer(pattern, source))
    if len(matches) != 13:
        raise ValueError(f'Expected 10 chapters and 3 supplements, got {len(matches)}')
    parts = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        parts.append((match.group(1), source[match.end():end].strip()))
    intro = source[:matches[0].start()]
    intro = re.sub(r'^# [^\n]+\n', '', intro)
    intro = re.sub(r'(?m)^### (.+)$', r'\1', intro).strip()
    intro_html = f'''<section class="lesson-section overview-section" id="overview" aria-labelledby="overview-title"><header class="section-header"><span class="section-number" aria-hidden="true">序</span><div class="section-title-wrap"><p class="section-kicker">开始之前</p><h2 id="overview-title">这节课，怎样学才有用？</h2></div></header><div class="chapter-content prose">{render_markdown(adapt_scope(intro))}</div></section>'''
    toc = ['<p class="toc-group-label">学习准备</p><ul class="toc-list"><li><a class="toc-link" data-label="学习前的准备" href="#overview"><span class="toc-index">序</span><span>这节课怎样学</span></a></li></ul><p class="toc-group-label">十个基础小节</p><ol class="toc-list">']
    chapters = []
    illustrations = {4: states_figure(), 5: conservation_figure(), 7: energy_figure()}
    for index, (title, body) in enumerate(parts[:10], 1):
        body = adapt_scope(body)
        number = f'{index:02d}'
        section_id = f'chapter-{number}'
        title = re.sub(r'^## 第[一二三四五六七八九十]+讲：', '', title)
        toc.append(f'<li><a class="toc-link" data-label="第 {index} 小节，{SHORT_TITLES[index-1]}" href="#{section_id}"><span class="toc-index">{number}</span><span>{SHORT_TITLES[index-1]}</span></a></li>')
        next_id = f'chapter-{index+1:02d}' if index < 10 else 'observations'
        next_label = '下一个小节' if index < 10 else '去做两个小观察'
        chapters.append(f'''<section class="lesson-section" id="{section_id}" data-chapter="{index}" aria-labelledby="{section_id}-title">
<header class="section-header"><span class="section-number" aria-hidden="true">{number}</span><div class="section-title-wrap"><p class="section-kicker">第一课 / 第 {index} 小节</p><h2 id="{section_id}-title">{html.escape(title)}</h2><p class="section-summary">{SUMMARIES[index-1]}</p></div></header>
<div class="chapter-content"><div class="prose">{render_markdown(body)}</div>{illustrations.get(index, '')}<div class="chapter-end"><button class="complete-button js-only" type="button" data-complete="{section_id}" aria-pressed="false" aria-label="标记第 {index} 小节已完成"><span class="check-box" aria-hidden="true"></span><span class="button-label">标记本节已完成</span></button><a class="next-section" href="#{next_id}">{next_label} <span aria-hidden="true">→</span></a></div></div></section>''')
    toc.append('</ol><p class="toc-group-label">理解与应用</p><ul class="toc-list">')
    extra_data = [('observations', '观', '两个生活观察', '不追求热闹效果，练习区分现象与结论。'), ('self-check', '问', '五道理解自测', '先用自己的话回答，再展开看看理解要点。'), ('next-steps', '续', '把基础带进生活', '选择一个真正让你好奇的方向，继续往下走。')]
    supplements = []
    for (title, body), (section_id, mark, short_title, summary) in zip(parts[10:], extra_data):
        body = adapt_scope(body)
        toc.append(f'<li><a class="toc-link" data-label="{short_title}" href="#{section_id}"><span class="toc-index">{mark}</span><span>{short_title}</span></a></li>')
        body = re.sub(r'(?m)^## ', '### ', body)
        if section_id == 'self-check':
            table = re.search(r'(?m)^\| 问题 \| 理解要点 \|\n(?:\|[^\n]*\n?)+', body)
            if not table:
                raise ValueError('Self-check table not found')
            rows = table.group(0).strip().splitlines()[2:]
            details = ['<span class="sr-only">问题 理解要点</span>']
            for q_index, row in enumerate(rows, 1):
                question, answer = [cell.strip() for cell in row.strip('|').split('|')]
                details.append(f'<details class="answer"><summary><span class="answer-num">问题 {q_index:02d} / 05</span>{html.escape(question)}</summary><div class="answer-body">{html.escape(answer)}</div></details>')
            before = render_markdown(body[:table.start()])
            after = render_markdown(body[table.end():])
            content = before + '<p class="answer-hint">点击问题展开理解要点；不计分，也不需要背诵。</p>' + ''.join(details) + after
        else:
            content = render_markdown(body)
        supplements.append(f'''<section class="lesson-section supplement" id="{section_id}" aria-labelledby="{section_id}-title"><header class="section-header"><span class="section-number" aria-hidden="true">{mark}</span><div class="section-title-wrap"><p class="section-kicker">第一课 / 理解与应用</p><h2 id="{section_id}-title">{html.escape(title[2:])}</h2><p class="section-summary">{summary}</p></div></header><div class="chapter-content prose">{content}</div></section>''')
    toc.append('</ul>')
    data = {
        'CSS': (ROOT / 'src/course.css').read_text(encoding='utf-8'),
        'JS': (ROOT / 'src/course.js').read_text(encoding='utf-8'),
        'TOC': ''.join(toc), 'INTRO': intro_html,
        'CHAPTERS': '\n'.join(chapters), 'SUPPLEMENTS': '\n'.join(supplements),
        'MARKDOWN_DATA': 'data:text/markdown;charset=utf-8;base64,' + base64.b64encode(source.encode('utf-8')).decode('ascii'),
    }
    page = (ROOT / 'src/lesson-01.template.html').read_text(encoding='utf-8')
    for key, value in data.items():
        page = page.replace(f'@@{key}@@', value)
    if re.search(r'@@[A-Z_]+@@', page):
        raise ValueError('Unresolved template marker')
    target = ROOT / 'lesson-01.html'
    target.write_text(page, encoding='utf-8')
    print(f'Built {target.name}: {target.stat().st_size:,} bytes; 10 chapters, 5 self-checks, 15 sources.')


if __name__ == '__main__':
    build()
