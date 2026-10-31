# Publish your own repository

The public repository is [charrus/esphome-eyocean-lamp](https://github.com/charrus/esphome-eyocean-lamp). This guide covers reviewing local changes and publishing your own copy; its commands do not run automatically. When contributing to the existing repository, use its configured remote rather than creating it again.

## Before making it public

- Choose a license and add the appropriate license file. No license has been selected yet; public visibility is not the same as an open-source license.
- Review all example values. Keep the runnable YAML examples at `remote_id: 0x0000` and `xor_key: 0x00` by default. The four user-reported known-working pairs in the documentation were explicitly supplied for publication; do not add other remote identities without their owner's permission.
- Keep only placeholder credentials in `examples/secrets.yaml.example`. Never publish an actual `secrets.yaml`, API/OTA keys, Wi-Fi credentials, personal addresses, or unreviewed logs.
- Check `.gitignore` excludes private secrets and build artifacts. Ignore rules do not remove files already tracked by Git.
- Review every tracked file and any existing commit history for secrets. If credentials were previously committed, revoke/rotate them and clean the history before publishing; deleting the working-tree file alone is insufficient.
- Keep the documented limits: protocol-family support, no lamp feedback, no automatic learning or recording/playback, independent proxy TX, and no completed physical verification of the sanitized examples.

Run local checks after installing requirements and creating a private secrets file:

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
esphome config examples/t-embed-cc1101.yaml
esphome compile examples/t-embed-cc1101.yaml
```

Validate and compile any other examples you intend to claim as tested. Compilation may download toolchains, dependencies, and fonts. Do not describe a compile or synthetic test pass as a successful flash or physical lamp test.

## Inspect and commit locally

Run in the repository root. If this directory is not already a Git repository, initialize it first:

```sh
git init
```

Review the working tree and tracked paths:

```sh
git status --short
git ls-files
```

Stage only reviewed public files. For the initial project layout:

```sh
git add README.md docs packages examples tests .github .gitignore requirements-dev.txt
git diff --cached --stat
git diff --cached
```

Review the complete staged diff before committing. Add a selected license file separately if you created one. Do not use blanket staging until you have verified ignore rules and untracked files.

```sh
git commit -m "Prepare EYOCEAN ESPHome lamp configuration"
```

## Create the public GitHub repository

Install GitHub CLI (`gh`) using the [official installation instructions](https://cli.github.com/). It was not installed in the preparation environment. Authenticate locally; do not share credentials in chat:

```sh
gh auth login
gh auth status
```

The next command **creates a public repository and pushes your local commits**. Run it yourself only after the review above, from the repository root:

```sh
gh repo create esphome-eyocean-lamp --public --source . --remote origin --push
```

This assumes the target repository does not already exist and no conflicting `origin` remote is configured. Check existing remotes first with `git remote -v`; inspect any conflict rather than overwriting it blindly.

Verify the actual published target and contents:

```sh
gh repo view --json nameWithOwner,url,visibility
git remote -v
git status --short
```

Open the returned URL and inspect the files, rendered README links, commit history, visibility, and absence of secrets/build artifacts. Only after publication should you add a real GitHub URL or remote-package/import instructions, and those instructions must be tested against the published layout.

No commit, push, repository creation, flashing, or existing device modification is implied by these instructions.
