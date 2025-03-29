import os
import logging
import shutil
import re
import git
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def get_repository_name(repo_url):
    """
    Extract repository name from URL
    """
    parsed_url = urlparse(repo_url)
    path = parsed_url.path.strip('/')
    
    # Handle both username/repo and org/repo formats
    if path:
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[-1]
    
    # Fallback to the last part of the URL
    return path.split('/')[-1] if path else "unknown-repo"

def clone_repository(repo_url, target_dir):
    """
    Clone a git repository to a specified directory
    
    Args:
        repo_url (str): The URL of the repository to clone
        target_dir (str): The directory to clone the repository to
        
    Returns:
        str: The path to the cloned repository
    """
    logger.info(f"Cloning repository {repo_url} to {target_dir}")
    
    # Ensure the target directory exists
    if os.path.exists(target_dir):
        logger.info(f"Cleaning up existing directory: {target_dir}")
        shutil.rmtree(target_dir)
    
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        # Clone the repository
        git.Repo.clone_from(repo_url, target_dir)
        logger.info(f"Repository cloned successfully to {target_dir}")
        return target_dir
    except git.GitCommandError as e:
        logger.error(f"Failed to clone repository: {str(e)}")
        raise Exception(f"Failed to clone repository: {str(e)}")

def cleanup_repository(repo_path):
    """
    Clean up a cloned repository
    
    Args:
        repo_path (str): The path to the repository to clean up
    """
    if os.path.exists(repo_path):
        logger.info(f"Cleaning up repository: {repo_path}")
        shutil.rmtree(repo_path)
    else:
        logger.warning(f"Repository path does not exist: {repo_path}")

def list_files(repo_path, exclude_patterns=None):
    """
    List all files in a repository, optionally excluding files matching patterns
    
    Args:
        repo_path (str): The path to the repository
        exclude_patterns (list): List of regex patterns to exclude
        
    Returns:
        list: List of file paths relative to repo_path
    """
    if exclude_patterns is None:
        exclude_patterns = [
            r'\.git/',
            r'node_modules/',
            r'__pycache__/',
            r'\.venv/',
            r'\.env/',
            r'\.DS_Store',
            r'\.idea/',
            r'\.vscode/',
            r'\.png$',
            r'\.jpg$',
            r'\.jpeg$',
            r'\.gif$',
            r'\.svg$',
            r'\.pdf$',
            r'\.zip$',
            r'\.tar$',
            r'\.gz$'
        ]
    
    # Compile exclude patterns
    compiled_patterns = [re.compile(pattern) for pattern in exclude_patterns]
    
    file_list = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(pattern.search(os.path.join(root, d, '')) for pattern in compiled_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_path)
            
            # Skip excluded files
            if any(pattern.search(relative_path) for pattern in compiled_patterns):
                continue
                
            file_list.append(relative_path)
    
    return file_list
