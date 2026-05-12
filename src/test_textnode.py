import unittest

from htmlnode import LeafNode
from textnode import (
    TextNode,
    TextType,
    text_node_to_html_node,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_url_default_none(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT, None)
        self.assertEqual(node, node2)

    def test_different_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_different_url(self):
        node = TextNode("This is a text node", TextType.LINK, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.LINK, "https://example.com")
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("b", "Bold text"))

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("i", "Italic text"))

    def test_code(self):
        node = TextNode("Code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("code", "Code text"))

    def test_link(self):
        node = TextNode("anchor text", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node,
            LeafNode("a", "anchor text", {"href": "https://www.boot.dev"}),
        )

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, "https://example.com/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node,
            LeafNode(
                "img",
                "",
                {"src": "https://example.com/image.png", "alt": "alt text"},
            ),
        )

    def test_invalid_type(self):
        node = TextNode("unknown", "bad type")
        with self.assertRaises(Exception):
            text_node_to_html_node(node)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_single(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode(
            "This is text with no images",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_images_image_at_start(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) with text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" with text after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images_image_at_end(self):
        node = TextNode(
            "Text before ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Text before ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_images_only_image(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_images_three_images(self):
        node = TextNode(
            "![img1](url1.png) text ![img2](url2.png) more ![img3](url3.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("img1", TextType.IMAGE, "url1.png"),
                TextNode(" text ", TextType.TEXT),
                TextNode("img2", TextType.IMAGE, "url2.png"),
                TextNode(" more ", TextType.TEXT),
                TextNode("img3", TextType.IMAGE, "url3.png"),
            ],
            new_nodes,
        )

    def test_split_images_preserves_non_text_nodes(self):
        node1 = TextNode("bold text", TextType.BOLD)
        node2 = TextNode(
            "This has an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node1, node2])
        self.assertListEqual(
            [
                TextNode("bold text", TextType.BOLD),
                TextNode("This has an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_links_single(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )

    def test_split_links_no_links(self):
        node = TextNode(
            "This is text with no links",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links_link_at_start(self):
        node = TextNode(
            "[link text](https://example.com) with text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link text", TextType.LINK, "https://example.com"),
                TextNode(" with text after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_link_at_end(self):
        node = TextNode(
            "Text before [link text](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Text before ", TextType.TEXT),
                TextNode("link text", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_only_link(self):
        node = TextNode(
            "[link text](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link text", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_three_links(self):
        node = TextNode(
            "[link1](url1) text [link2](url2) more [link3](url3)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link1", TextType.LINK, "url1"),
                TextNode(" text ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "url2"),
                TextNode(" more ", TextType.TEXT),
                TextNode("link3", TextType.LINK, "url3"),
            ],
            new_nodes,
        )

    def test_split_links_preserves_non_text_nodes(self):
        node1 = TextNode("italic text", TextType.ITALIC)
        node2 = TextNode(
            "This has a [link](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node1, node2])
        self.assertListEqual(
            [
                TextNode("italic text", TextType.ITALIC),
                TextNode("This has a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )



    def test_text_to_textnodes_complex(self):
        """Test the main example from the assignment"""
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_text_to_textnodes_only_text(self):
        """Test with plain text only"""
        text = "This is plain text"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is plain text", TextType.TEXT)],
            nodes,
        )

    def test_text_to_textnodes_only_bold(self):
        """Test with only bold text"""
        text = "**bold**"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)],
            nodes,
        )

    def test_text_to_textnodes_multiple_bold(self):
        """Test with multiple bold sections"""
        text = "**bold1** text **bold2**"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold1", TextType.BOLD),
                TextNode(" text ", TextType.TEXT),
                TextNode("bold2", TextType.BOLD),
            ],
            nodes,
        )

    def test_text_to_textnodes_all_formats(self):
        """Test with all formatting types"""
        text = "**bold** _italic_ `code` ![image](url) [link](href)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "url"),
                TextNode(" ", TextType.TEXT),
                TextNode("link", TextType.LINK, "href"),
            ],
            nodes,
        )

    def test_text_to_textnodes_multiple_links_images(self):
        """Test with multiple links and images"""
        text = "[link1](url1) and ![img1](img1) and [link2](url2)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("link1", TextType.LINK, "url1"),
                TextNode(" and ", TextType.TEXT),
                TextNode("img1", TextType.IMAGE, "img1"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "url2"),
            ],
            nodes,
        )

    def test_text_to_textnodes_empty_string(self):
        """Test with empty string"""
        text = ""
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("", TextType.TEXT)],
            nodes,
        )

    def test_text_to_textnodes_image_with_complex_url(self):
        """Test image with complex URL"""
        text = "Before ![alt text with spaces](https://example.com/path/to/image.png?query=value) after"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Before ", TextType.TEXT),
                TextNode("alt text with spaces", TextType.IMAGE, "https://example.com/path/to/image.png?query=value"),
                TextNode(" after", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_bold_and_code(self):
        """Test bold and code together"""
        text = "**bold** and `code` together"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" together", TextType.TEXT),
            ],
            nodes,
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


if __name__ == "__main__":
    unittest.main()