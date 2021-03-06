# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Presubmit script for devil.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into depot_tools.
"""


def _RunPylint(input_api, output_api):
  return input_api.canned_checks.RunPylint(
      input_api,
      output_api,
      pylintrc='pylintrc',
      extra_paths_list=[
          input_api.os_path.join(input_api.PresubmitLocalPath(), '..'),
      ])


def _RunUnitTests(input_api, output_api):
  def J(*dirs):
    """Returns a path relative to presubmit directory."""
    return input_api.os_path.join(input_api.PresubmitLocalPath(), *dirs)

  test_env = dict(input_api.environ)
  test_env.update({
    'PYTHONDONTWRITEBYTECODE': '1',
    'PYTHONPATH': ':'.join([J(), J('..')]),
  })

  return input_api.canned_checks.RunUnitTests(
      input_api,
      output_api,
      unit_tests=[
          J('devil_env_test.py'),
          J('android', 'battery_utils_test.py'),
          J('android', 'device_utils_test.py'),
          J('android', 'fastboot_utils_test.py'),
          J('android', 'md5sum_test.py'),
          J('android', 'logcat_monitor_test.py'),
          J('android', 'tools', 'script_common_test.py'),
          J('utils', 'cmd_helper_test.py'),
          J('utils', 'timeout_retry_unittest.py'),
      ],
      env=test_env)


def _EnsureNoPylibUse(input_api, output_api):
  def other_python_files(f):
    this_presubmit_file = input_api.os_path.join(
        input_api.PresubmitLocalPath(), 'PRESUBMIT.py')
    return (f.LocalPath().endswith('.py')
            and not f.AbsoluteLocalPath() == this_presubmit_file)

  changed_files = input_api.AffectedSourceFiles(other_python_files)
  import_error_re = input_api.re.compile(
      r'(from pylib.* import)|(import pylib)')

  errors = []
  for f in changed_files:
    errors.extend(
        '%s:%d' % (f.LocalPath(), line_number)
        for line_number, line_text in f.ChangedContents()
        if import_error_re.search(line_text))

  if errors:
    return [output_api.PresubmitError(
        'pylib modules should not be imported from devil modules.',
        items=errors)]
  return []


def _TemporarilyReadOnly(input_api, output_api):
  # Temporarily make devil/ read-only for the move to catapult.
  # TODO(jbudorick): Remove this after the move is complete.

  def other_files(f):
    this_presubmit_file = input_api.os_path.join(
        input_api.PresubmitLocalPath(), 'PRESUBMIT.py')
    return not f.AbsoluteLocalPath() == this_presubmit_file

  changed_files = input_api.AffectedSourceFiles(other_files)
  if changed_files:
    return [output_api.PresubmitError(
        'devil/ is temporarily read-only while it moves to catapult. '
        'Questions? Contact jbudorick@',
        items=changed_files)]
  return []


def CommonChecks(input_api, output_api):
  output = []
  output += _RunPylint(input_api, output_api)
  output += _RunUnitTests(input_api, output_api)
  output += _EnsureNoPylibUse(input_api, output_api)
  output += _TemporarilyReadOnly(input_api, output_api)
  return output


def CheckChangeOnUpload(input_api, output_api):
  return CommonChecks(input_api, output_api)


def CheckChangeOnCommit(input_api, output_api):
  return CommonChecks(input_api, output_api)
