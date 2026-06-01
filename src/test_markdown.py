import unittest

from textnode import TextNode, TextType
from inline_markdown import (
    markdown_to_blocks,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    block_to_block_type,
    BlockType,
    markdown_to_html_node,
)


class TestSplitNodesDelimiter(unittest.TestCase):

    def test_code(self):
        node = TextNode(
            "This is text with a `code block` word",
            TextType.TEXT,
        )

        result = split_nodes_delimiter(
            [node],
            "`",
            TextType.CODE,
        )

        self.assertEqual(
            result,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode(
            "This is **bold** text",
            TextType.TEXT,
        )

        result = split_nodes_delimiter(
            [node],
            "**",
            TextType.BOLD,
        )

        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode(
            "This is _italic_ text",
            TextType.TEXT,
        )

        result = split_nodes_delimiter(
            [node],
            "_",
            TextType.ITALIC,
        )

        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_multiple_delimiters(self):
        node = TextNode(
            "`one` and `two`",
            TextType.TEXT,
        )

        result = split_nodes_delimiter(
            [node],
            "`",
            TextType.CODE,
        )

        self.assertEqual(
            result,
            [
                TextNode("one", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("two", TextType.CODE),
            ],
        )

    def test_no_delimiter(self):
        node = TextNode(
            "plain text",
            TextType.TEXT,
        )

        result = split_nodes_delimiter(
            [node],
            "`",
            TextType.CODE,
        )

        self.assertEqual(
            result,
            [
                TextNode("plain text", TextType.TEXT),
            ],
        )

    def test_invalid_markdown(self):
        node = TextNode(
            "This is `broken markdown",
            TextType.TEXT,
        )

        with self.assertRaises(Exception):
            split_nodes_delimiter(
                [node],
                "`",
                TextType.CODE,
            )

    def test_non_text_node(self):
        node = TextNode(
            "already code",
            TextType.CODE,
        )

        result = split_nodes_delimiter(
            [node],
            "`",
            TextType.CODE,
        )

        self.assertEqual(
            result,
            [
                TextNode("already code", TextType.CODE),
            ],
        )

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

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

    def test_extract_markdown_links(self):
        matches = extract_markdown_links("This is a [Google](https://google.com) link")
        self.assertListEqual(
            [("Google", "https://google.com")],
            matches,
        )

    def test_split_links(self):
        node = TextNode(
            "Go to [Google](https://google.com) and [GitHub](https://github.com)",
            TextType.TEXT,
        )

        new_nodes = split_nodes_link([node])

        self.assertListEqual(
            [
                TextNode("Go to ", TextType.TEXT),
                TextNode("Google", TextType.LINK, "https://google.com"),
                TextNode(" and ", TextType.TEXT),
                TextNode("GitHub", TextType.LINK, "https://github.com"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes_full(self):

        text = (
            "This is **text** with an _italic_ word and a `code block` "
            "and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) "
            "and a [link](https://boot.dev)"
        )

        result = text_to_textnodes(text)

        self.assertListEqual(
            result,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
        )

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

    def test_heading(self):
        self.assertEqual(
            block_to_block_type("# Heading"),
            BlockType.HEADING,
        )
        self.assertEqual(
            block_to_block_type("###### Small heading"),
            BlockType.HEADING,
        )

    def test_code(self):
        self.assertEqual(
            block_to_block_type("```\ncode here\n```"),
            BlockType.CODE,
        )

    def test_quote(self):
        self.assertEqual(
            block_to_block_type("> quote line\n> another quote"),
            BlockType.QUOTE,
        )
        self.assertEqual(
            block_to_block_type(">quote without space"),
            BlockType.QUOTE,
        )

    def test_unordered_list(self):
        self.assertEqual(
            block_to_block_type("- item one\n- item two"),
            BlockType.ULIST,
        )

    def test_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. first\n2. second\n3. third"),
            BlockType.OLIST,
        )

    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("just a normal paragraph"),
            BlockType.PARAGRAPH,
        )

    def test_not_ordered_list_if_wrong_numbering(self):
        self.assertEqual(
            block_to_block_type("1. one\n3. three"),
            BlockType.PARAGRAPH,
        )

    def test_paragraphs(self):
        md = """
        This is **bolded** paragraph
        text in a p
        tag here

        This is another paragraph with _italic_ text and `code` here

        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
        ```
        This is text that _should_ remain
        the **same** even with inline stuff
        ```
        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_ulist(self):
        md = """
    - Apple
    - Banana
    - Cherry
    """

        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(
            html,
            "<div><ul><li>Apple</li><li>Banana</li><li>Cherry</li></ul></div>",
        )

    def test_markdown_to_blocks_list_and_paragraph_separation(self):

        md = """
    - You can spend years studying the legendarium and still not understand its depths
    - It can be enjoyed by children and adults alike
    - Disney didn't ruin it (okay, but Amazon might have)
    - It created an entirely new genre of fantasy

    This is another paragraph with _italic_ text and `code` here
    This is the same paragraph on a new line
    """

        blocks = markdown_to_blocks(md)

        self.assertEqual(
            blocks,
            [
                "- You can spend years studying the legendarium and still not understand its depths\n- It can be enjoyed by children and adults alike\n- Disney didn't ruin it (okay, but Amazon might have)\n- It created an entirely new genre of fantasy",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
            ],
        )

    def test_ulist_paragraph_split(self):
        from inline_markdown import markdown_to_html_node

        md = """
    - You can spend years studying the legendarium and still not understand its depths
    - It can be enjoyed by children and adults alike
    - Disney didn't ruin it (okay, but Amazon might have)
    - It created an entirely new genre of fantasy

    This is another paragraph with _italic_ text and `code` here
    """

        html = markdown_to_html_node(md).to_html()

        self.assertIn("<ul>", html)
        self.assertIn("</ul>", html)
        self.assertIn("<li>It can be enjoyed by children and adults alike</li>", html)


if __name__ == "__main__":
    unittest.main()
