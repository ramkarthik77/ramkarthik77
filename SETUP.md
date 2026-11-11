# GitHub Profile Setup

The repository name must match your GitHub username: `ramkarthik77`.

The README and animated SVG cards render natively on your public profile.

## First synchronization

1. Open the **Actions** tab of this repository.
2. Select **Refresh profile graphics**.
3. Click **Run workflow** and choose `main`.
4. Reload the profile after it finishes.

The built-in `GITHUB_TOKEN` reads contribution data and pushes updated SVGs. No separate credential is required. The workflow also runs daily at 06:23 UTC.

If the workflow cannot push, navigate to **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, then retry. Repository or organization policies may limit this setting.

GitHub may automatically disable scheduled workflows after a period of repository inactivity. If that happens, re-enable the workflow in the Actions tab.

## Design

The hero and project graphics are static animated SVGs; contribution graphics are generated from GitHub's GraphQL contribution calendar. No private enterprise/project metrics are used. All project links reference public repositories.

## Edit

- Profile text: `README.md`
- Hero art: `assets/hero.svg`
- Project cards: `assets/project-*.svg`
- Live stats renderer: `scripts/render.py`
- Scheduled refresh: `.github/workflows/update-profile.yml`
