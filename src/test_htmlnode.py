import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode
from inline_markdown import markdown_to_html_node


class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_single(self):
        node = HTMLNode(
            tag="a", value="click me", props={"href": "https://example.com"}
        )
        self.assertEqual(node.props_to_html(), 'href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(
            tag="a",
            value="click me",
            props={"href": "https://example.com", "target": "_blank"},
        )
        result = node.props_to_html()

        # order is not guaranteed in dict, so test flexibly
        self.assertIn('href="https://example.com"', result)
        self.assertIn('target="_blank"', result)
        self.assertEqual(len(result.split()), 2)

    def test_props_to_html_none(self):
        node = HTMLNode(tag="p", value="hello world", props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_lead_to_html_a(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )


if __name__ == "__main__":
    unittest.main()
