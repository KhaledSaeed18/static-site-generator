import re
from enum import Enum

from htmlnode import LeafNode


class TextType(Enum):
	TEXT = "text"
	BOLD = "bold"
	ITALIC = "italic"
	CODE = "code"
	LINK = "link"
	IMAGE = "image"

class BlockType(Enum):
	PARAGRAPH = "paragraph"
	HEADING = "heading"
	CODE = "code"
	QUOTE = "quote"
	UNORDERED_LIST = "unordered_list"
	ORDERED_LIST = "ordered_list"


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


def extract_markdown_images(text):
	return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
	return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
	"""Split TextType.TEXT nodes by extracted markdown images.
	
	Returns a new list where images are extracted into TextType.IMAGE nodes
	and text segments remain as TextType.TEXT nodes.
	"""
	new_nodes = []
	
	for node in old_nodes:
		# Only operate on raw text nodes
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
			continue
		
		# Extract images from the text
		images = extract_markdown_images(node.text)
		if not images:
			# No images found, keep the node as-is
			new_nodes.append(node)
			continue
		
		# Split text at each image
		text = node.text
		for image_alt, image_url in images:
			sections = text.split(f"![{image_alt}]({image_url})", 1)
			
			# Add the text before the image (if not empty)
			if sections[0] != "":
				new_nodes.append(TextNode(sections[0], TextType.TEXT))
			
			# Add the image node
			new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_url))
			
			# Update text to process remaining parts
			if len(sections) > 1:
				text = sections[1]
			else:
				text = ""
		
		# Add any remaining text (if not empty)
		if text != "":
			new_nodes.append(TextNode(text, TextType.TEXT))
	
	return new_nodes


def split_nodes_link(old_nodes):
	"""Split TextType.TEXT nodes by extracted markdown links.
	
	Returns a new list where links are extracted into TextType.LINK nodes
	and text segments remain as TextType.TEXT nodes.
	"""
	new_nodes = []
	
	for node in old_nodes:
		# Only operate on raw text nodes
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
			continue
		
		# Extract links from the text
		links = extract_markdown_links(node.text)
		if not links:
			# No links found, keep the node as-is
			new_nodes.append(node)
			continue
		
		# Split text at each link
		text = node.text
		for link_text, link_url in links:
			sections = text.split(f"[{link_text}]({link_url})", 1)
			
			# Add the text before the link (if not empty)
			if sections[0] != "":
				new_nodes.append(TextNode(sections[0], TextType.TEXT))
			
			# Add the link node
			new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
			
			# Update text to process remaining parts
			if len(sections) > 1:
				text = sections[1]
			else:
				text = ""
		
		# Add any remaining text (if not empty)
		if text != "":
			new_nodes.append(TextNode(text, TextType.TEXT))
	
	return new_nodes


def text_to_textnodes(text):
	"""Convert raw markdown text to a list of TextNode objects.
	
	Processes the text through all splitting functions in sequence:
	- Bold (**text**)
	- Italic (_text_)
	- Code (`text`)
	- Images (![alt](url))
	- Links ([text](url))
	"""
	nodes = [TextNode(text, TextType.TEXT)]
	nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
	nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
	nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
	nodes = split_nodes_image(nodes)
	nodes = split_nodes_link(nodes)
	return nodes


def markdown_to_blocks(markdown):
	"""Split a markdown string into blocks.
	
	Blocks are separated by blank lines (\n\n). Each block is stripped of
	leading/trailing whitespace. Empty blocks are removed.
	
	Args:
		markdown: A raw markdown string representing a full document
	
	Returns:
		A list of block strings
	"""
	# Split by double newlines
	blocks = markdown.split("\n\n")
	
	# Strip each block and filter out empty ones
	filtered_blocks = []
	for block in blocks:
		stripped = block.strip()
		if stripped:
			filtered_blocks.append(stripped)
	
	return filtered_blocks


def block_to_block_type(block):
	"""Determine the type of a markdown block.
	
	Args:
		block: A single block of markdown text (with leading/trailing whitespace already stripped)
	
	Returns:
		A BlockType enum value representing the type of block
	"""
	lines = block.split("\n")
	
	# Check for heading (1-6 # followed by space)
	if re.match(r"^#{1,6} ", block):
		return BlockType.HEADING
	
	# Check for code block (starts with ``` and ends with ```)
	if block.startswith("```") and block.endswith("```"):
		return BlockType.CODE
	
	# Check for quote (every line starts with >)
	if all(line.startswith(">") for line in lines):
		return BlockType.QUOTE
	
	# Check for unordered list (every line starts with - followed by space)
	if all(line.startswith("- ") for line in lines):
		return BlockType.UNORDERED_LIST
	
	# Check for ordered list (every line starts with number. followed by space, incrementing from 1)
	is_ordered_list = True
	for i, line in enumerate(lines):
		expected_number = i + 1
		if not re.match(rf"^{expected_number}\. ", line):
			is_ordered_list = False
			break
	
	if is_ordered_list:
		return BlockType.ORDERED_LIST
	
	# Default to paragraph
	return BlockType.PARAGRAPH
