# Add SciPy Dependency for Projection Models

We decided to add `scipy` as a core dependency in `pyproject.toml`. While the current linear rolling baseline model does not strictly require it (and we could compute Spearman correlation manually using Pearson on ranks), upcoming scientific and statistical projection models in the pipeline will heavily rely on SciPy's numerical capabilities, making it a necessary foundational library for the project's analytical goals.
