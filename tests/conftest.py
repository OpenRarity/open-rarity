def pytest_addoption(parser):
    parser.addoption(
        "--run-resolvers",
        action="store_true",
        default=False,
        help="Run slow resolver tests",
    )
