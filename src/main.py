import os
import shutil

from textnode import markdown_to_html_node


def copy_directory_contents(source_dir, destination_dir):
	if os.path.exists(destination_dir):
		shutil.rmtree(destination_dir)

	os.mkdir(destination_dir)

	for entry in os.listdir(source_dir):
		source_path = os.path.join(source_dir, entry)
		destination_path = os.path.join(destination_dir, entry)

		if os.path.isfile(source_path):
			print(f"Copying file: {source_path} -> {destination_path}")
			shutil.copy(source_path, destination_path)
		else:
			copy_directory_contents(source_path, destination_path)


def extract_title(markdown):
	for line in markdown.splitlines():
		stripped_line = line.strip()
		if stripped_line.startswith("# ") and not stripped_line.startswith("##"):
			return stripped_line[2:].strip()

	raise Exception("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
	print(f"Generating page from {from_path} to {dest_path} using {template_path}")

	with open(from_path, "r", encoding="utf-8") as markdown_file:
		markdown = markdown_file.read()

	with open(template_path, "r", encoding="utf-8") as template_file:
		template = template_file.read()

	content = markdown_to_html_node(markdown).to_html()
	title = extract_title(markdown)

	page = template.replace("{{ Title }}", title).replace("{{ Content }}", content)

	destination_dir = os.path.dirname(dest_path)
	if destination_dir:
		os.makedirs(destination_dir, exist_ok=True)

	with open(dest_path, "w", encoding="utf-8") as output_file:
		output_file.write(page)


def generate_pages_recursive(content_dir, template_path, public_dir):
	for entry in os.listdir(content_dir):
		content_path = os.path.join(content_dir, entry)

		if os.path.isfile(content_path) and content_path.endswith(".md"):
			destination_path = os.path.join(public_dir, entry[:-3] + ".html")
			generate_page(content_path, template_path, destination_path)
		elif os.path.isdir(content_path):
			child_public_dir = os.path.join(public_dir, entry)
			os.makedirs(child_public_dir, exist_ok=True)
			generate_pages_recursive(content_path, template_path, child_public_dir)


def main():
	copy_directory_contents("static", "public")
	generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
	main()