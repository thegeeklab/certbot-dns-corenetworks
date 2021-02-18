local PythonVersion(pyversion='3.6') = {
  name: 'python' + std.strReplace(pyversion, '.', '') + '-pytest',
  image: 'python:' + pyversion,
  environment: {
    PY_COLORS: 1,
  },
  commands: [
    'pip install poetry poetry-dynamic-versioning -qq',
    'poetry config experimental.new-installer false',
    'poetry install',
    'poetry run pytest',
    'poetry version',
  ],
  depends_on: [
    'fetch',
  ],
};

local PipelineLint = {
  kind: 'pipeline',
  name: 'lint',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'yapf',
      image: 'python:3.9',
      environment: {
        PY_COLORS: 1,
      },
      commands: [
        'git fetch -tq',
        'pip install poetry poetry-dynamic-versioning -qq',
        'poetry install',
        'poetry run yapf -dr ./certbot_dns_corenetworks',
      ],
    },
    {
      name: 'flake8',
      image: 'python:3.9',
      environment: {
        PY_COLORS: 1,
      },
      commands: [
        'git fetch -tq',
        'pip install poetry poetry-dynamic-versioning -qq',
        'poetry install',
        'poetry run flake8 ./certbot_dns_corenetworks',
      ],
    },
  ],
  trigger: {
    ref: ['refs/heads/main', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineTest = {
  kind: 'pipeline',
  name: 'test',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'fetch',
      image: 'python:3.9',
      commands: [
        'git fetch -tq',
      ],
    },
    PythonVersion(pyversion='3.6'),
    PythonVersion(pyversion='3.7'),
    PythonVersion(pyversion='3.8'),
    PythonVersion(pyversion='3.9'),
    {
      name: 'codecov',
      image: 'python:3.9',
      environment: {
        PY_COLORS: 1,
        CODECOV_TOKEN: { from_secret: 'codecov_token' },
      },
      commands: [
        'pip install codecov -qq',
        'codecov --required -X gcov',
      ],
      depends_on: [
        'python36-pytest',
        'python37-pytest',
        'python38-pytest',
        'python39-pytest',
      ],
    },
  ],
  depends_on: [
    'lint',
  ],
  trigger: {
    ref: ['refs/heads/main', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineSecurity = {
  kind: 'pipeline',
  name: 'security',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'bandit',
      image: 'python:3.9',
      environment: {
        PY_COLORS: 1,
      },
      commands: [
        'git fetch -tq',
        'pip install poetry poetry-dynamic-versioning -qq',
        'poetry install',
        'poetry run bandit -r ./certbot_dns_corenetworks -x ./certbot_dns_corenetworks/test',
      ],
    },
  ],
  depends_on: [
    'test',
  ],
  trigger: {
    ref: ['refs/heads/main', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineBuildPackage = {
  kind: 'pipeline',
  name: 'build-package',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'build',
      image: 'python:3.9',
      commands: [
        'git fetch -tq',
        'pip install poetry poetry-dynamic-versioning -qq',
        'poetry build',
      ],
    },
    {
      name: 'checksum',
      image: 'alpine',
      commands: [
        'cd dist/ && sha256sum * > ../sha256sum.txt',
      ],
    },
    {
      name: 'publish-github',
      image: 'plugins/github-release',
      settings: {
        overwrite: true,
        api_key: { from_secret: 'github_token' },
        files: ['dist/*', 'sha256sum.txt'],
        title: '${DRONE_TAG}',
        note: 'CHANGELOG.md',
      },
      when: {
        ref: ['refs/tags/**'],
      },
    },
    {
      name: 'publish-pypi',
      image: 'python:3.9',
      commands: [
        'git fetch -tq',
        'pip install poetry poetry-dynamic-versioning -qq',
        'poetry publish -n',
      ],
      environment: {
        POETRY_HTTP_BASIC_PYPI_USERNAME: { from_secret: 'pypi_username' },
        POETRY_HTTP_BASIC_PYPI_PASSWORD: { from_secret: 'pypi_password' },
      },
      when: {
        ref: ['refs/tags/**'],
      },
    },
  ],
  depends_on: [
    'security',
  ],
  trigger: {
    ref: ['refs/heads/main', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineNotifications = {
  kind: 'pipeline',
  name: 'notifications',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'matrix',
      image: 'plugins/matrix',
      settings: {
        homeserver: { from_secret: 'matrix_homeserver' },
        roomid: { from_secret: 'matrix_roomid' },
        template: 'Status: **{{ build.status }}**<br/> Build: [{{ repo.Owner }}/{{ repo.Name }}]({{ build.link }}) ({{ build.branch }}) by {{ build.author }}<br/> Message: {{ build.message }}',
        username: { from_secret: 'matrix_username' },
        password: { from_secret: 'matrix_password' },
      },
      when: {
        status: ['success', 'failure'],
      },
    },
  ],
  depends_on: [
    'build-package',
  ],
  trigger: {
    ref: ['refs/heads/main', 'refs/tags/**'],
    status: ['success', 'failure'],
  },
};

[
  PipelineLint,
  PipelineTest,
  PipelineSecurity,
  PipelineBuildPackage,
  PipelineNotifications,
]
