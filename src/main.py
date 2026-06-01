import os
import shutil
import sys

from inline_markdown import generate_page


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    if not os.path.exists(dest_dir_path):
        os.makedirs(dest_dir_path)

    for item in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, item)
        dst_path = os.path.join(dest_dir_path, item)

        if os.path.isfile(src_path) and src_path.endswith(".md"):
            html_path = dst_path.replace(".md", ".html")
            generate_page(src_path, template_path, html_path, basepath)

        elif os.path.isdir(src_path):
            generate_pages_recursive(src_path, template_path, dst_path, basepath)


def copy_static(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)

    os.mkdir(dst)

    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isfile(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Copied: {src_path} → {dst_path}")

        else:
            copy_static(src_path, dst_path)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_static("static", "docs")
    # generate_page("content/index.md", "template.html", "public/index.html")
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
