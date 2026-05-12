import os
import shutil


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


def main():
	copy_directory_contents("static", "public")


main()