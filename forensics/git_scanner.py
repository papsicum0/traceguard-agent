import os
import git

def extract_commit_authors(repo_path: str = ".", max_commits: int = 50) -> dict:
    clean_path = os.path.abspath(repo_path)
    
    try:
        repo = git.Repo(clean_path, search_parent_directories=True)
    except (git.exc.InvalidGitRepositoryError, git.exc.NoSuchPathError):
        return {
            "success": False,
            "error": f"No valid Git repository located at: {clean_path}",
            "authors": []
        }

    if not repo.heads:
        return {
            "success": True,
            "error": None,
            "authors": [],
            "message": "Repository initialized but contains zero commits."
        }

    authors = set()
    try:
        ref_names = [ref.name for ref in repo.references]
        if "origin/main" in ref_names:
            commits = list(repo.iter_commits("origin/main..HEAD"))
            if not commits:
                commits = list(repo.iter_commits(max_count=max_commits))
        else:
            commits = list(repo.iter_commits(max_count=max_commits))

        for commit in commits:
            if commit.author and commit.author.email:
                authors.add(commit.author.email.strip().lower())

    except (git.exc.GitCommandError, ValueError) as e:
        try:
            head_commit = repo.head.commit
            if head_commit.author and head_commit.author.email:
                authors.add(head_commit.author.email.strip().lower())
        except Exception:
            return {
                "success": False, 
                "error": f"Git metadata unreadable: {str(e)}", 
                "authors": []
            }

    return {
        "success": True,
        "error": None,
        "authors": list(authors)
    }
