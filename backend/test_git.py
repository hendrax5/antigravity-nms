import os
import shutil
import logging
from app.core.git_manager import GitManager

logging.basicConfig(level=logging.INFO)

def test_git_manager():
    tenant_id = 999
    repo_path = f"/app/config_backups/tenant_{tenant_id}"
    
    # Clean up old test data if any
    if os.path.exists("/app/config_backups"):
        shutil.rmtree("/app/config_backups")
        
    print("--- Running GitManager Tests ---")
    
    # 1. Initialize without remote (Local only for testing)
    git_manager = GitManager(tenant_id=tenant_id, repo_url="")
    
    # Override _ensure_repo_ready to create a local-only mock repo since we don't have a real remote URL
    import git
    os.makedirs(git_manager.local_path, exist_ok=True)
    repo = git.Repo.init(git_manager.local_path)
    git_manager._ensure_repo_ready = lambda: repo
    
    hostname = "SW-TEST-01"
    
    # 2. Test First Commit
    config_v1 = "hostname SW-TEST-01\ninterface vlan 1\nip address 10.0.0.1 255.255.255.0\n"
    committed_1 = git_manager.commit_device_config(hostname, config_v1, "Initial backup")
    print(f"First commit successful: {committed_1}")
    assert committed_1 is True, "First commit should have changes"
    
    # 3. Test No-Changes Commit
    committed_no_change = git_manager.commit_device_config(hostname, config_v1, "Should be ignored")
    print(f"No-change commit ignored correctly: {not committed_no_change}")
    assert committed_no_change is False, "Exact same config should not trigger a commit"
    
    # 4. Test Second Commit
    config_v2 = config_v1 + "interface vlan 2\nip address 192.168.1.1 255.255.255.0\n"
    committed_2 = git_manager.commit_device_config(hostname, config_v2, "Added VLAN 2")
    print(f"Second commit successful: {committed_2}")
    assert committed_2 is True, "Modified config should trigger a commit"
    
    # 5. Fetch History
    history = git_manager.get_commit_history(hostname)
    print(f"History Length: {len(history)} commits found.")
    assert len(history) == 2, "History should contain exactly 2 commits"
    
    # 6. Fetch Content at specific commit
    oldest_commit_hash = history[1]['commit_hash']
    retrieved_content = git_manager.get_file_content_at_commit(hostname, oldest_commit_hash)
    print(f"Retrieved v1 content matches original: {retrieved_content == config_v1}")
    assert retrieved_content == config_v1, "Failed to retrieve exact content from Git history"
    
    print("--- All GitManager Tests Passed Successfully! ---")

if __name__ == "__main__":
    test_git_manager()
