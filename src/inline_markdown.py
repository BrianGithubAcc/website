from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import ParentNode, LeafNode
import re
import os
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    ULIST = "ulist"
    OLIST = "olist"


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError("invalid markdown syntax")

        new_nodes.extend(
            TextNode(part, TextType.TEXT) if i % 2 == 0 else TextNode(part, text_type)
            for i, part in enumerate(parts)
            if part != ""
        )

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text

        while True:
            match = re.search(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

            if not match:
                if text:
                    new_nodes.append(TextNode(text, TextType.TEXT))
                break

            if match.start() > 0:
                new_nodes.append(TextNode(text[: match.start()], TextType.TEXT))

            new_nodes.append(TextNode(match.group(1), TextType.IMAGE, match.group(2)))
            text = text[match.end() :]

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text

        while True:
            match = re.search(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

            if not match:
                if text:
                    new_nodes.append(TextNode(text, TextType.TEXT))
                break

            if match.start() > 0:
                new_nodes.append(TextNode(text[: match.start()], TextType.TEXT))

            new_nodes.append(TextNode(match.group(1), TextType.LINK, match.group(2)))
            text = text[match.end() :]

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    for delimiter, ttype in [
        ("**", TextType.BOLD),
        ("_", TextType.ITALIC),
        ("`", TextType.CODE),
    ]:
        nodes = split_nodes_delimiter(nodes, delimiter, ttype)

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_blocks(markdown):
    lines = markdown.split("\n")

    blocks = []
    current = []

    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)

    if current:
        blocks.append("\n".join(current).strip())

    return blocks


def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.lstrip().startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.lstrip().startswith("- ") for line in lines if line.strip()):
        return BlockType.ULIST

    nums = [
        int(re.match(r"^(\d+)\. ", line).group(1))
        for line in lines
        if re.match(r"^\d+\. ", line)
    ]

    if nums and nums == list(range(1, len(nums) + 1)):
        return BlockType.OLIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    return [text_node_to_html_node(n) for n in text_to_textnodes(text)]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            text = " ".join(line.strip() for line in block.split("\n"))
            children.append(ParentNode("p", text_to_children(text)))

        elif block_type == BlockType.HEADING:
            level = len(block.split(" ")[0])
            text = block[level + 1 :]
            children.append(ParentNode(f"h{level}", text_to_children(text)))

        elif block_type == BlockType.CODE:
            code_lines = block.split("\n")[1:-1]
            code_text = "\n".join(code_lines) + "\n"
            code = LeafNode("code", code_text)
            children.append(ParentNode("pre", [code]))

        elif block_type == BlockType.QUOTE:
            text = "\n".join(line.lstrip("> ").strip() for line in block.split("\n"))
            children.append(ParentNode("blockquote", text_to_children(text)))

        elif block_type == BlockType.ULIST:
            items = [
                ParentNode("li", text_to_children(line[2:].strip()))
                for line in block.split("\n")
                if line.startswith("- ")
            ]
            children.append(ParentNode("ul", items))

        elif block_type == BlockType.OLIST:
            items = [
                ParentNode("li", text_to_children(line.split(". ", 1)[1]))
                for line in block.split("\n")
            ]
            children.append(ParentNode("ol", items))

    return ParentNode("div", children)


def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No H1 header found")


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    # FIX: apply basepath correctly
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page)
