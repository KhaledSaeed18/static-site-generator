from enum import Enum

from htmlnode import LeafNode


class TextType(Enum):
	TEXT = "text"
	BOLD = "bold"
	ITALIC = "italic"
	CODE = "code"
	LINK = "link"
	IMAGE = "image"


class TextNode:
	def __init__(self, text, text_type, url=None):
		self.text = text
		self.text_type = text_type
		self.url = url

	def __eq__(self, other):
		if not isinstance(other, TextNode):
			return False

		return (
			self.text == other.text
			and self.text_type == other.text_type
			and self.url == other.url
		)

	def __repr__(self):
		return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
	if text_node.text_type == TextType.TEXT:
		return LeafNode(None, text_node.text)
	if text_node.text_type == TextType.BOLD:
		return LeafNode("b", text_node.text)
	if text_node.text_type == TextType.ITALIC:
		return LeafNode("i", text_node.text)
	if text_node.text_type == TextType.CODE:
		return LeafNode("code", text_node.text)
	if text_node.text_type == TextType.LINK:
		return LeafNode("a", text_node.text, {"href": text_node.url})
	if text_node.text_type == TextType.IMAGE:
		return LeafNode(
			"img",
			"",
			{"src": text_node.url, "alt": text_node.text},
		)

	raise Exception("Unsupported text type")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
	"""Split any TextType.TEXT nodes in old_nodes by the given delimiter.

	Returns a new list of TextNode objects where text sections between
	delimiter pairs become nodes with text_type, and other text remains as TEXT.
	Raises Exception on unmatched delimiter.
	"""
	new_nodes = []

	for node in old_nodes:
		# Only operate on raw text nodes
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
			continue

		parts = node.text.split(delimiter)
		# No delimiter found, keep node as-is
		if len(parts) == 1:
			new_nodes.append(node)
			continue

		n_delims = len(parts) - 1
		# delimiters must come in pairs
		if n_delims % 2 != 0:
			raise Exception(f"Unmatched delimiter '{delimiter}' in text: {node.text}")

		for i, part in enumerate(parts):
			if i % 2 == 0:
				# plain text segment
				if part != "":
					new_nodes.append(TextNode(part, TextType.TEXT))
			else:
				# delimited segment becomes the provided text_type
				new_nodes.append(TextNode(part, text_type))

	return new_nodes
