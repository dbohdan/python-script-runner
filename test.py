#! /usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

RUNNER = "python-script-runner"
SCRIPT = "script.py"

SCRIPT_PERMS = 0o700


@contextmanager
def temp_runner_context():
    """Create a temporary directory with the meta-runner script."""
    with tempfile.TemporaryDirectory() as temp_dir_str:
        env_path = os.environ.get("PATH", "")
        temp_dir = Path(temp_dir_str)

        # `printf` is necessary on OpenBSD.
        for command in ("basename", "printf"):
            os.symlink(shutil.which(command), temp_dir / command)

        os.environ["PATH"] = temp_dir_str

        try:
            # Copy the script to the temporary directory.
            shutil.copy2(Path(__file__).parent / RUNNER, temp_dir / RUNNER)
            (temp_dir / RUNNER).chmod(SCRIPT_PERMS)

            yield temp_dir, env_path

        finally:
            os.environ["PATH"] = env_path


def create_fake_runner(temp_dir: Path, name: str, exit_code: int = 0) -> None:
    """Create a fake runner that prints its name and arguments."""
    fake_runner = temp_dir / name
    fake_runner.write_text(rf"""#! /bin/sh
printf '%s\n' "$@"
exit {exit_code}
""")
    fake_runner.chmod(SCRIPT_PERMS)


class TestPythonScriptRunner(unittest.TestCase):
    def test_uv(self):
        with temp_runner_context() as (temp_dir, _original_path):
            for runner in ("uv", "pipx"):
                create_fake_runner(temp_dir, runner)

            # Create a test script.
            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            # Run the test script.
            result = subprocess.run(
                [str(test_script), "arg1", "arg2"],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # Check the exit code and the output.
            self.assertEqual(result.returncode, 0)

            output_lines = result.stdout.splitlines()
            self.assertEqual(
                output_lines,
                ["run", "--script", "--", str(test_script), "arg1", "arg2"],
            )

    def test_pipx(self):
        with temp_runner_context() as (temp_dir, _original_path):
            for runner in ("pipx", "hatch"):
                create_fake_runner(temp_dir, runner)

            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            result = subprocess.run(
                [str(test_script), "arg1", "arg2"],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)

            output_lines = result.stdout.splitlines()
            self.assertEqual(
                output_lines,
                ["run", "--path", "--", str(test_script), "arg1", "arg2"],
            )

    def test_hatch(self):
        with temp_runner_context() as (temp_dir, _original_path):
            for runner in ("hatch", "pip-run"):
                create_fake_runner(temp_dir, runner)

            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            result = subprocess.run(
                [str(test_script), "arg1", "arg2"],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)

            output_lines = result.stdout.splitlines()
            self.assertEqual(
                output_lines,
                ["run", "--", str(test_script), "arg1", "arg2"],
            )

    def test_pip_run(self):
        with temp_runner_context() as (temp_dir, _original_path):
            create_fake_runner(temp_dir, "pip-run")

            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            result = subprocess.run(
                [str(test_script), "arg1", "arg2"],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)

            output_lines = result.stdout.splitlines()
            self.assertEqual(
                output_lines,
                ["--", str(test_script), "arg1", "arg2"],
            )

    def test_preference_order(self):
        with temp_runner_context() as (temp_dir, _original_path):
            # Create every fake runner.
            for runner in ("uv", "pipx", "hatch", "pip-run"):
                create_fake_runner(temp_dir, runner)

            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            result = subprocess.run(
                [str(test_script), "foo"],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            self.assertEqual(result.returncode, 0)

            output_lines = result.stdout.splitlines()
            self.assertEqual(
                output_lines,
                ["run", "--script", "--", str(test_script), "foo"],
            )

    def test_no_runners(self):
        with temp_runner_context() as (temp_dir, _original_path):
            # Do not create any fake runners.

            test_script = temp_dir / SCRIPT
            test_script.write_text(f"""#! /usr/bin/env {RUNNER}
print("test")
""")
            test_script.chmod(SCRIPT_PERMS)

            result = subprocess.run(
                [str(test_script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=temp_dir,
            )

            # python-script-runner exits with a particular exit code
            # when no runners are found.
            self.assertEqual(result.returncode, 127)
            # Check that the error message is printed on stderr.
            self.assertIn("No compatible Python script runner found", result.stderr)


if __name__ == "__main__":
    unittest.main()
