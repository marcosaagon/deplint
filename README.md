# deplint

Static analyzer for Python dependency files that detects version conflicts, deprecated packages, and license issues.

## Installation

```bash
pip install deplint
```

## Usage

Run `deplint` against your requirements file:

```bash
deplint requirements.txt
```

Example output:

```
Analyzing requirements.txt...

[WARN]  requests==2.18.0       — outdated (latest: 2.31.0)
[ERROR] urllib3==1.24.1        — version conflict with requests>=2.28.0
[INFO]  PyYAML==5.4.1          — license: MIT (ok)
[WARN]  somepackage==1.0.0     — deprecated, see migration guide

3 issues found (1 error, 2 warnings)
```

You can also scan `pyproject.toml` or `setup.cfg`:

```bash
deplint pyproject.toml
deplint setup.cfg
```

### Options

| Flag | Description |
|------|-------------|
| `--strict` | Exit with non-zero code on warnings |
| `--ignore-licenses` | Skip license checks |
| `--format json` | Output results as JSON |
| `--fix` | Auto-upgrade outdated packages in file |

```bash
deplint requirements.txt --strict --format json
```

## License

MIT © deplint contributors