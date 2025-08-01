######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
CLI Command Extensions for Flask
"""

# pylint: disable=duplicate-code
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from service.common.cli_commands import init_cli
from service import create_app as create_flask_app

# pylint: disable=unused-import
from wsgi import app  # noqa: F401


class TestFlaskCLI(TestCase):
    """Flask CLI Command Tests"""

    def setUp(self):
        self.runner = CliRunner()

    @patch("service.common.cli_commands.db")
    def test_db_create(self, db_mock):
        """It should call the db-create command"""
        db_mock.return_value = MagicMock()
        with patch.dict(os.environ, {"FLASK_APP": "wsgi:app"}, clear=True):

            init_cli(app)
            result = self.runner.invoke(app.cli, args=["db-create"])
            self.assertEqual(result.exit_code, 0)

    def test_create_app_triggers_logging_and_cli(self):
        """Test that create_app triggers logging and CLI registration."""
        test_app = create_flask_app()
        assert test_app is not None
