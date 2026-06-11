# PR Handoff Guard Policy

Use this reference when a worker opens or updates a pull request and the task may be retried.

## Problem

Some automation treats raw PR URLs in retryable text as an active PR marker. A retry may be suppressed or confused if the handoff only contains a bare URL with no structured state.

## Guard-Safe Handoff

Use explicit fields:

```text
PR_REF: owner/repo#number
BRANCH: branch-name
BASE: base-branch
HEAD_SHA: commit-sha
PR_POLICY: update_existing_before_opening_new
```

Include the URL only as supporting context, not the sole machine-readable field.

## Worker Rule

Before opening a new PR, check whether a PR already exists for the branch. If one exists, update it instead of creating a duplicate.

## Review Rule

Reviewers should verify the branch/head SHA they reviewed and mention it in the verdict.
