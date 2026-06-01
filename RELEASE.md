Release checklist and Zenodo archiving

1. Clean the repository
   - Remove any large intermediate files not needed for reproducibility.
   - Ensure `requirements.txt` lists all Python dependencies.

2. Add metadata
   - Update `CITATION.cff` with author names, affiliation, and repository URL.
   - Consider adding a `README` badge with DOI after archiving.

3. Tag a release on GitHub
   - Push your changes and create a Git tag, e.g. `v0.1.0`.
   - Create a GitHub Release with the tag and a short description.

4. Enable Zenodo integration and archive
   - Go to https://zenodo.org/ and link your GitHub repo (Account → GitHub integrations).
   - Select the repository and enable automatic archiving on new releases.
   - After creating the GitHub release, Zenodo will mint a DOI.

5. Update repository
   - Add the DOI to `README.md` and `CITATION.cff` (`doi:` field).
   - Add a `CITATION` or `CITATION.cff` file (already present).

6. Final checks
   - Verify that the minted DOI resolves to the release and includes the proper files.
   - Upload supplementary data directly to Zenodo if needed.
