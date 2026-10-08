import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.assets, self.sections, self.buttons = [], [], [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ('script', 'img', 'iframe', 'link'):
            url = attrs.get('src') or attrs.get('href')
            if url:
                self.assets.append(url)
        if tag == 'section' and 'data-chapter' in attrs:
            self.sections.append(attrs)
        if tag == 'button' and 'data-complete' in attrs:
            self.buttons.append(attrs)


class CourseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'lesson-01.html').read_text(encoding='utf-8')
        cls.source = (ROOT / '化学入门教程.md').read_text(encoding='utf-8')
        cls.page = Page(cls.html)

    def test_ten_chapters_and_supplements(self):
        self.assertEqual(len(self.page.sections), 10)
        self.assertEqual(len(self.page.buttons), 10)
        for section in ('overview', 'observations', 'self-check', 'next-steps'):
            self.assertIn(section, self.page.ids)

    def test_unique_ids_and_working_internal_links(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        for link in self.page.links:
            if link.startswith('#'):
                self.assertIn(link[1:], self.page.ids)

    def test_all_sources_preserved(self):
        sources = re.findall(r'\]\((https://[^)]+)\)', self.source)
        self.assertEqual(len(sources), 15)
        for source in sources:
            self.assertIn(source, self.page.links)

    def test_no_external_dependencies(self):
        self.assertEqual(self.page.assets, [])
        self.assertNotIn('@import', self.html)
        self.assertNotIn('fetch(', self.html)

    def test_original_source_embedded_for_download(self):
        import base64
        payload = re.search(r'href="data:text/markdown;charset=utf-8;base64,([^"]+)"', self.html)
        self.assertIsNotNone(payload)
        self.assertEqual(base64.b64decode(payload.group(1)).decode('utf-8'), self.source)

    def test_accessibility_and_fallbacks(self):
        self.assertIn('lang="zh-CN"', self.html)
        self.assertIn('<noscript>', self.html)
        self.assertIn('prefers-reduced-motion', self.html)
        self.assertIn('@media print', self.html)
        self.assertEqual(self.html.count('class="answer"'), 5)
        for button in self.page.buttons:
            self.assertEqual(button['aria-pressed'], 'false')

    def test_all_original_prose_is_visible_html(self):
        from html import unescape
        from tools.build_course import render_markdown, adapt_scope
        class Text(HTMLParser):
            def __init__(self, text):
                super().__init__()
                self.parts = []
                self.feed(text)
            def handle_data(self, data):
                self.parts.append(data)
        def plain(text):
            return re.sub(r'\s+', '', ''.join(Text(text).parts))
        document = plain(self.html)
        for paragraph in re.split(r'\n\s*\n', self.source):
            paragraph = adapt_scope(paragraph)
            if paragraph.startswith('#') or paragraph.strip() == '---':
                continue
            if paragraph.startswith('|'):
                for row in paragraph.splitlines():
                    if re.match(r'^\|[-| ]+\|$', row):
                        continue
                    for cell in row.strip('|').split('|'):
                        text = plain(render_markdown(cell.strip()))
                        self.assertIn(text, document)
                continue
            expected = plain(render_markdown(paragraph))
            self.assertIn(expected, document)


if __name__ == '__main__':
    unittest.main()
