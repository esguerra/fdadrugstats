# Deployment to GitHub Pages

This repository publishes generated results to GitHub Pages using the `docs/` folder. The site is automatically deployed on push to `main` by the workflow defined in `.github/workflows/pages.yml`.

## How the workflow works ⚙️

- On push to `main` (or when manually triggered), the workflow:
  1. Checks out the repository
  2. Installs Python and the project dependencies (`pip install -r requirements.txt`)
  3. Runs `python src/main.py` to generate the latest CSVs and PNGs in `results/` (the workflow picks up the `FDA_API_KEY` from `secrets.FDA_API_KEY` if set)
  4. Runs `python scripts/sync_results.py` to copy the generated files into `docs/results/`
  5. Uploads `docs/` to GitHub Pages

> Tip: If you prefer to generate results locally, run `python src/main.py` and commit the updated `results/` files. The workflow will copy them into `docs/` and deploy.

## Custom domain setup (fdadrugstats.mesguerra.org) 🌐

The site includes a `docs/CNAME` file with the chosen domain. To point the domain at GitHub Pages:

1. In your DNS provider, create a CNAME record:
   - Host: `fdadrugstats` (or `@` depending on provider)
   - Value: `<your-github-username>.github.io.`

2. Alternatively, for apex domains (root domain), add the recommended GitHub Pages A records (see GitHub Pages docs).

3. In the repository Settings → Pages, ensure the custom domain is set (it's automatically read from `CNAME`) and enable "Enforce HTTPS" once the certificate is available.

## Secrets

- If you have an FDA API key, add it to the repository secrets as `FDA_API_KEY` to avoid rate limits. The workflow will read this secret when it runs.

## Manual synchronization

- To copy results into `docs/` locally:

```
python src/main.py
python scripts/sync_results.py --force
```

The `--force` flag overwrites existing files in `docs/results/`.
