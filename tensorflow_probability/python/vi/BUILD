# Copyright 2018 The TensorFlow Probability Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
# Description:
#   Methods and objectives for variational inference.

# [internal] load python3.bzl

licenses(["notice"])  # Apache 2.0

package(
    default_visibility = [
        "//tensorflow_probability:__subpackages__",
    ],
)

exports_files(["LICENSE"])

py_library(
    name = "vi",
    srcs = ["__init__.py"],
    srcs_version = "PY2AND3",
    deps = [
        ":csiszar_divergence",
    ],
)

py_library(
    name = "csiszar_divergence",
    srcs = ["csiszar_divergence.py"],
    srcs_version = "PY2AND3",
    deps = [
        # numpy dep,
        # tensorflow dep,
        "//tensorflow_probability/python/distributions",
        "//tensorflow_probability/python/internal:nest_util",
        "//tensorflow_probability/python/monte_carlo",
    ],
)

py_test(
    name = "csiszar_divergence_test",
    size = "medium",
    srcs = ["csiszar_divergence_test.py"],
    shard_count = 5,
    deps = [
        # numpy dep,
        # tensorflow dep,
        "//tensorflow_probability",
        "//tensorflow_probability/python/internal:test_case",
        "//tensorflow_probability/python/internal:test_util",
    ],
)
