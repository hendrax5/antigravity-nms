import os
import git
import logging
from typing import List, Dict, Any
from git.exc import GitCommandError

logger = logging.getLogger(__name__)

# Base directory inside the Docker container to store local repo clones
BASE_REPO_DIR = "/app/config_backups"

class GitManager:
    """
    Handles cloning, committing, and retrieving configuration history from Git repositories.
    """
    def __init__(self, tenant_id: int, repo_url: str, branch: str = "main", token: str = None):
        self.tenant_id = tenant_id
        self.repo_url = self._inject_token(repo_url, token) if token else repo_url
        self.branch = branch
        self.local_path = os.path.join(BASE_REPO_DIR, f"tenant_{tenant_id}")

    def _inject_token(self, url: str, token: str) -> str:
        """Injects personal access token into HTTPS URL for auth."""
        if "https://" in url:
            return url.replace("https://", f"https://oauth2:{token}@")
        return url

    def _ensure_repo_ready(self) -> git.Repo:
        """Clones the repo if not exists, otherwise pulls the latest changes."""
        if not os.path.exists(self.local_path):
            os.makedirs(self.local_path, exist_ok=True)
            try:
                logger.info(f"Cloning repo for Tenant {self.tenant_id} into {self.local_path}")
                repo = git.Repo.clone_from(self.repo_url, self.local_path, branch=self.branch)
                return repo
            except GitCommandError as e:
                logger.error(f"Failed to clone repository: {str(e)}")
                raise
        else:
            try:
                repo = git.Repo(self.local_path)
                repo.remotes.origin.pull(self.branch)
                return repo
            except GitCommandError as e:
                logger.error(f"Failed to pull repository updates: {str(e)}")
                raise

    def commit_device_config(self, hostname: str, config_content: str, commit_message: str = "Automated config backup") -> bool:
        """
        Writes the device configuration to a file and commits it if there are changes.
        """
        try:
            repo = self._ensure_repo_ready()
            
            # Save configuration to a file named after the device
            file_path = os.path.join(self.local_path, f"{hostname}.conf")
            with open(file_path, "w") as f:
                f.write(config_content)
                
            # Add and check for diffs
            repo.index.add([f"{hostname}.conf"])
            
            if not repo.is_dirty():
                logger.info(f"No configuration changes detected for {hostname}. Skipping commit.")
                return False
                
            # Commit and push
            repo.index.commit(commit_message)
            repo.remotes.origin.push()
            logger.info(f"Successfully backed up configuration for {hostname}")
            return True
            
        except Exception as e:
            logger.error(f"Error during git commit operation for {hostname}: {str(e)}")
            return False

    def get_commit_history(self, hostname: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves the commit history for a specific device configuration file.
        """
        try:
            repo = self._ensure_repo_ready()
            filename = f"{hostname}.conf"
            
            commits = list(repo.iter_commits(paths=filename, max_count=limit))
            history = []
            
            for commit in commits:
                history.append({
                    "commit_hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip()
                })
                
            return history
        except Exception as e:
            logger.error(f"Failed to get git history for {hostname}: {str(e)}")
            return []

    def get_file_content_at_commit(self, hostname: str, commit_hash: str) -> str:
        """
        Retrieves the exact content of the configuration file at a specific Git commit hash.
        """
        try:
            repo = self._ensure_repo_ready()
            filename = f"{hostname}.conf"
            commit = repo.commit(commit_hash)
            target_file = commit.tree / filename
            return target_file.data_stream.read().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to read file content at commit {commit_hash}: {str(e)}")
            return ""
