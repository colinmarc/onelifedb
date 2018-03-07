import os
import re

import git

repo = git.Repo('OneLifeData7')
repo.config_reader()


def _parse_tag(s):
    if s == 'OneLife_vStart':
        return 0

    match = re.match(r"OneLife_v(\d+)", s)
    if not match:
        raise ValueError("Invalid version tag: {}".format(s))

    return int(match.group(1))


def _tag_commits(t):
    return set((t.commit,)) | set(t.commit.iter_parents())


def load_object_versions(path):
    repo = git.Repo('OneLifeData7')
    repo.config_reader()

    object_to_commit = {}
    for commit in repo.iter_commits():
        try:
            parent = commit.iter_parents().next()
        except StopIteration:
            next

        new_files = (diff.b_path for diff in parent.diff(commit)
                     if diff.new_file or diff.rename_to)
        for path in new_files:
            data_type, fn = os.path.split(path)
            if data_type == 'objects' and re.match(r"\d+\.txt", fn):
                object_to_commit[int(fn[:-4])] = commit

    version_to_commits = {_parse_tag(tag.name): _tag_commits(tag)
                          for tag in repo.tags}

    commit_to_version = {}
    for commit in set(object_to_commit.values()):
        versions = [v for v, history in version_to_commits.items()
                    if commit in history]
        if not versions:
            v = None
        else:
            v = min(versions)

        commit_to_version[commit] = v

    return {oid: commit_to_version[commit]
            for oid, commit in object_to_commit.items()}
