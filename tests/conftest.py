""" Pytest configuration. """


def pytest_addoption(parser):
    """ Add configuration options to pytest. """
    parser.addoption(
        "--lint-only",
        action="store_true",
        default=False,
        help="Only run linting checks",
    )


def pytest_collection_modifyitems(session, config, items):
    # pylint: disable=unused-argument
    """ Override options in case of 'lint-only' option. """
    if config.getoption("--lint-only"):
        lint_items = []
        for linter in ["flake8", "mypy", "pylint"]:
            if config.getoption(f"--{linter}"):
                lint_items.extend(
                    [item for item in items if item.get_closest_marker(linter)]
                )
        items[:] = lint_items
