import os
import base64
import requests

GITHUB_TOKEN = "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"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def push_to_github():
    print("Fetching user info...")
    user_resp = requests.get("https://api.github.com/user", headers=HEADERS)
    user_resp.raise_for_status()
    username = user_resp.json()["login"]
    print(f"Logged in as {username}")

    repo_name = "antigravity-nms"
    print(f"Creating repository {repo_name}...")
    repo_resp = requests.post("https://api.github.com/user/repos", headers=HEADERS, json={
        "name": repo_name,
        "private": True,
        "auto_init": True
    })
    
    if repo_resp.status_code == 422: # Already exists
        print("Repository already exists. Proceeding to push to it.")
    else:
        repo_resp.raise_for_status()
        print("Repository created successfully.")

    cwd = os.getcwd()
    # List of files to push (we will use the same logic as build_zip.py)
    exclude_dirs = ['node_modules', '__pycache__', '.pytest_cache', '.git', 'dist', '.venv', 'venv']
    
    tree_items = []
    
    # Just to be safe, only push a subset or use the zip?
    # No, Coolify needs the raw files.
    # Uploading blobs limits: let's upload text files as utf-8 and binaries as base64.
    
    print("Uploading blobs...")
    for root, dirs, files in os.walk(cwd):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.zip') or file.endswith('.pyc') or file == 'build_zip.py':
                continue
            
            file_path = os.path.join(root, file)
            # Relative path to repo root
            rel_path = os.path.relpath(file_path, cwd).replace('\\', '/')
            
            with open(file_path, "rb") as f:
                content = f.read()
                
            # Create Blob
            blob_resp = requests.post(f"https://api.github.com/repos/{username}/{repo_name}/git/blobs", headers=HEADERS, json={
                "content": base64.b64encode(content).decode('utf-8'),
                "encoding": "base64"
            })
            blob_resp.raise_for_status()
            sha = blob_resp.json()["sha"]
            
            if file.endswith(".sh"):
                mode = "100755"
            else:
                mode = "100644"
                
            tree_items.append({
                "path": rel_path,
                "mode": mode,
                "type": "blob",
                "sha": sha
            })
            print(f"Uploaded blob for {rel_path} -> {sha}")

    print("Creating tree...")
    # Base tree usually is the current HEAD.
    # Let's get the master branch
    ref_resp = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/main", headers=HEADERS)
    if ref_resp.status_code == 404:
        ref_resp = requests.get(f"https://api.github.com/repos/{username}/{repo_name}/git/refs/heads/master", headers=HEADERS)
    ref_resp.raise_for_status()
    ref_info = ref_resp.json()
    base_tree_sha = ref_info["object"]["sha"]
    branch_ref = ref_info["ref"]

    tree_resp = requests.post(f"https://api.github.com/repos/{username}/{repo_name}/git/trees", headers=HEADERS, json={
        "base_tree": base_tree_sha,
        "tree": tree_items
    })
    tree_resp.raise_for_status()
    new_tree_sha = tree_resp.json()["sha"]
    print(f"Created tree {new_tree_sha}")

    print("Creating commit...")
    commit_resp = requests.post(f"https://api.github.com/repos/{username}/{repo_name}/git/commits", headers=HEADERS, json={
        "message": "Initial NMS deployment codebase via Antigravity Auto-Push",
        "tree": new_tree_sha,
        "parents": [base_tree_sha]
    })
    commit_resp.raise_for_status()
    new_commit_sha = commit_resp.json()["sha"]
    print(f"Created commit {new_commit_sha}")

    print("Updating reference...")
    update_resp = requests.patch(f"https://api.github.com/repos/{username}/{repo_name}/git/{branch_ref}", headers=HEADERS, json={
        "sha": new_commit_sha,
        "force": True
    })
    update_resp.raise_for_status()
    print("Branch updated. Push complete!")
    print(f"Repository URL: https://github.com/{username}/{repo_name}")

if __name__ == "__main__":
    push_to_github()
