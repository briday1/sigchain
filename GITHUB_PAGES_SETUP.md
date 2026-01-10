# Setting Up GitHub Pages for SigChain Demos

## Quick Setup

1. **Go to Repository Settings**
   - Navigate to https://github.com/briday1/sigchain/settings/pages

2. **Configure GitHub Pages**
   - Under "Source", select: **Deploy from a branch**
   - Under "Branch", select: **copilot/discuss-custom-blocks-framework** (or main after merge)
   - Under "Folder", select: **/docs**
   - Click **Save**

3. **Wait for Deployment**
   - GitHub Actions will automatically build and deploy the site
   - This usually takes 1-2 minutes

4. **Access Your Site**
   - Once deployed, the site will be available at:
     - https://briday1.github.io/sigchain/

## What Gets Published

The `docs/` directory contains:

- **docs/index.html** - Landing page with links to demos
- **docs/demo/** - Complete radar processing pipeline demo
- **docs/custom_demo/** - Custom block creation tutorial

All HTML files are self-contained with embedded Plotly visualizations.

## Updating the Demos

To regenerate the demos with new data or changes:

```bash
# Install dependencies (if not already installed)
pip install -e ".[visualization]"

# Run the demo generator
python examples/radar_plotly_dashboard.py

# Commit and push the updated docs/
git add docs/
git commit -m "Update interactive demos"
git push
```

GitHub Pages will automatically update within a few minutes.

## Custom Domain (Optional)

To use a custom domain:

1. Add a `docs/CNAME` file with your domain
2. Configure DNS settings with your domain provider
3. Enable HTTPS in GitHub Pages settings

## Troubleshooting

**Issue**: Page shows 404
- **Solution**: Make sure Branch is set correctly and /docs folder is selected

**Issue**: Plots don't show up
- **Solution**: Check browser console for errors. Plotly.js should be loading from CDN.

**Issue**: Changes not reflected
- **Solution**: Wait 1-2 minutes for GitHub Actions to redeploy, then hard refresh (Ctrl+F5)

## File Structure

```
docs/
├── index.html                    # Landing page
├── demo/                         # Main radar demo
│   ├── index.html               # Dashboard index
│   ├── pages/
│   │   └── radar-demo.html      # Full demo page
│   └── assets/                  # CSS, JS, and vendor files
│       ├── css/
│       ├── js/
│       └── vendor/
│           ├── plotly/          # Plotly.js
│           ├── prism/           # Code syntax highlighting
│           └── mathjax/         # Math rendering
└── custom_demo/                 # Custom blocks tutorial
    ├── index.html
    ├── pages/
    └── assets/
```

## Notes

- The total size of docs/ is approximately 11MB (mostly Plotly.js)
- All assets are self-contained (no external CDN dependencies for vendor libs)
- Dashboards are fully interactive with Plotly's pan, zoom, and hover features
- Works on all modern browsers (Chrome, Firefox, Safari, Edge)
