import unittest

from main import extract_title


class TestExtractTitle(unittest.TestCase):
	def test_extract_title(self):
		markdown = "# Hello"
		self.assertEqual(extract_title(markdown), "Hello")

	def test_extract_title_strips_whitespace(self):
		markdown = "#   Hello there   "
		self.assertEqual(extract_title(markdown), "Hello there")

	def test_extract_title_ignores_non_h1_headers(self):
		markdown = "## Not the title\n# Real Title"
		self.assertEqual(extract_title(markdown), "Real Title")

	def test_extract_title_raises_without_h1(self):
		markdown = "## Heading only\nParagraph"
		with self.assertRaises(Exception):
			extract_title(markdown)


if __name__ == "__main__":
	unittest.main()