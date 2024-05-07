# target-logic4

`target-logic4` is a Singer target for Logic4.

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
target is available by running:

```bash
target-logic4 --about
```

### Config file example

The config file is a json file and it needs to have public key, company key and username, secret_key and password,
the scope is optional if not set it will default to api administration.1:

```json
{
    "scope": "api administration.1",
    "public_key": "xxxxxxx",
    "company_key": "xxxxxxxxx",
    "username": "xxxxxxxxxx",
    "secret_key": "xxxxxxxxxx",
    "password": "xxxxxxxxx"
}

```

### Configure using environment variables

This Singer target will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `target-logic4` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Executing the Target Directly

Located in the virtual environment created run these commands.

```bash
target-logic4 --version
target-logic4 --help
target-logic4 < /path/to/data.singer --config path/to/config.json > target_state.json
```


