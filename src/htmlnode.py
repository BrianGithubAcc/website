from typing import override


class HTMLNode:
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: list["HTMLNode"] | None = None,
        props: dict[str, str] | None = None,
    ):
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: list["HTMLNode"] | None = children
        self.props: dict[str, str] | None = props

    def to_html(self) -> None:
        raise NotImplementedError

    def props_to_html(self) -> str:
        return (
            " ".join(f'{k}="{v}"' for k, v in self.props.items()) if self.props else ""
        )

    @override
    def __repr__(self) -> str:
        return f"Tag: {self.tag}\nValue: {self.value}\nChildren:{self.children}\nProps: {self.props}"


class LeafNode(HTMLNode):
    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        props: dict[str, str] | None = None,
    ):
        super().__init__(tag, value, None, props)

    @override
    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("LeafNode must have a value")

        if self.tag is None:
            return self.value

        attrs = self.props_to_html()
        attrs = f" {attrs}" if attrs else ""

        return f"<{self.tag}{attrs}>{self.value}</{self.tag}>"

    @override
    def __repr__(self) -> str:
        return f"Tag: {self.tag}\nValue: {self.value}\nProps: {self.props}"


class ParentNode(HTMLNode):

    def __init__(
        self, tag: str, children: list["HTMLNode"], props: dict[str, str] | None = None
    ):
        self.tag: str = tag
        self.children: list["HTMLNode"] = children
        self.props: dict[str, str] = props

    def to_html(self):
        if not self.tag:
            raise ValueError("Tag missing")
        if not self.children:
            raise ValueError("Miss Children")
        attrs = self.props_to_html()
        attrs = f" {attrs}" if attrs else ""

        return f"<{self.tag}{attrs}>{"".join(x.to_html() for x in self.children)}</{self.tag}>"

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
