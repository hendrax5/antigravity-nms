import os
import zipfile

def create_zip(source_dir, output_filename, exclude_dirs):
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.zip') or file.endswith('.log'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(source_dir))
                zipf.write(file_path, arcname)

if __name__ == '__main__':
    source = r'D:\antigravity'
    output = r'D:\antigravity\network-dashboard.zip'
    excludes = ['.git', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'dist']
    create_zip(source, output, excludes)
    print(f"Created {output} successfully.")
