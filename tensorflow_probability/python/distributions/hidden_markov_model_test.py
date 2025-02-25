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
"""The HiddenMarkovModel distribution class."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Dependency imports
from absl.testing import parameterized
import numpy as np
import tensorflow as tf
import tensorflow_probability as tfp

from tensorflow_probability.python.internal import test_util as tfp_test_util
tfd = tfp.distributions
from tensorflow.python.framework import test_util  # pylint: disable=g-direct-tensorflow-import,g-import-not-at-top

# pylint: disable=no-member


@test_util.run_all_in_graph_and_eager_modes
class _HiddenMarkovModelTest(
    tfp_test_util.VectorDistributionTestHelpers,
    tfp_test_util.DiscreteScalarDistributionTestHelpers,
    tf.test.TestCase,
    parameterized.TestCase):

  @staticmethod
  def make_placeholders(constants):
    return [
        tf.compat.v1.placeholder_with_default(constant, shape=None)
        for constant in constants
    ]

  def test_non_agreeing_states(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.6, 0.4],
                                          [0.3, 0.7]], dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0, 2.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    with self.assertRaisesWithPredicateMatch(Exception,
                                             lambda e: "must agree" in str(e)):
      model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                    tfd.Categorical(probs=transition_matrix),
                                    tfd.Normal(observation_locs,
                                               scale=observation_scale),
                                    num_steps=4,
                                    validate_args=True)
      self.evaluate(model.mean())

  def test_non_scalar_transition_batch(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    observation_locs_data = tf.constant(0.0, dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    with self.assertRaisesWithPredicateMatch(
        Exception,
        lambda e: "scalar batches" in str(e)):
      model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                    tfd.Categorical(probs=transition_matrix),
                                    tfd.Normal(observation_locs,
                                               scale=observation_scale),
                                    num_steps=4,
                                    validate_args=True)
      self.evaluate(model.mean())

  def test_consistency(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.6, 0.4],
                                          [0.3, 0.7]], dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=3,
                                  validate_args=True)

    self.run_test_sample_consistent_log_prob(self.evaluate, model,
                                             num_samples=100000,
                                             center=0.5, radius=0.5,
                                             rtol=0.05)

  def test_broadcast_initial_probs(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.6, 0.4],
                                          [0.3, 0.7]], dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=3)

    self.run_test_sample_consistent_log_prob(self.evaluate, model,
                                             num_samples=100000,
                                             center=0.5, radius=1.,
                                             rtol=0.02)

  def test_broadcast_transitions(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([[[0.8, 0.2],
                                           [0.3, 0.7]],
                                          [[0.9, 0.1],
                                           [0.2, 0.8]]],
                                         dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=3)

    self.run_test_sample_consistent_log_prob(self.evaluate, model,
                                             num_samples=100000,
                                             center=0.5, radius=1.,
                                             rtol=2e-2)

  def test_broadcast_observations(self):
    initial_prob_data = tf.constant([0.6, 0.4], dtype=self.dtype)
    transition_matrix_data = tf.constant([[[0.8, 0.2],
                                           [0.3, 0.7]],
                                          [[0.9, 0.1],
                                           [0.2, 0.8]]], dtype=self.dtype)
    observation_locs_data = tf.constant([[0.9, 0.1],
                                         [0.2, 0.8]], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=3)

    self.run_test_sample_consistent_log_prob(self.evaluate, model,
                                             num_samples=100000,
                                             center=0.5, radius=1.,
                                             rtol=2e-2)

  def test_edge_case_sample_n_no_transitions(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=1)

    x = model._sample_n(1)
    x_shape = self.evaluate(tf.shape(input=x))

    self.assertAllEqual(x_shape, [1, 1])

  def test_edge_case_log_prob_no_transitions(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])
    (initial_prob, transition_matrix,
     observation_probs) = ([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=1)

    x = model.log_prob([0])

    self.assertAllClose(x, np.log(0.5), rtol=1e-5, atol=0.0)

  def test_edge_case_mean_no_transitions(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=1)

    x = model.mean()
    x_shape = self.evaluate(tf.shape(input=x))

    self.assertAllEqual(x_shape, [1])

  def test_coin_tosses(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=5)

    x = model.log_prob([0, 0, 0, 0, 0])

    self.assertAllClose(x, np.log(.5**5), rtol=1e-5, atol=0.0)

  def test_coin_toss_batch(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    initial_prob = tf.broadcast_to(initial_prob, [3, 2, 2])
    transition_matrix = tf.broadcast_to(transition_matrix, [3, 2, 2, 2])
    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=5)

    examples = [tf.zeros(5, dtype=tf.int32), tf.ones(5, dtype=tf.int32)]
    examples = tf.broadcast_to(examples, [7, 3, 2, 5])
    computed_log_prob = model.log_prob(examples)

    expected_log_prob = tf.broadcast_to([np.log(.5**5)], [7, 3, 2])
    self.assertAllClose(computed_log_prob, expected_log_prob,
                        rtol=1e-4, atol=0.0)

  def test_batch_mean_shape(self):
    initial_prob_data = tf.constant([[0.8, 0.2],
                                     [0.5, 0.5],
                                     [0.2, 0.8]], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.7, 0.3],
                                          [0.2, 0.8]], dtype=self.dtype)
    observation_locs_data = tf.constant([[0.0, 0.0],
                                         [10.0, 10.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.MultivariateNormalDiag(
                                      loc=observation_locs),
                                  num_steps=7)

    x = model.mean()
    x_shape = self.evaluate(tf.shape(input=x))

    self.assertAllEqual(x_shape, [3, 7, 2])

  def test_mean_and_variance(self):
    initial_prob_data = tf.constant([0.6, 0.1, 0.3], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.2, 0.6, 0.2],
                                          [0.5, 0.3, 0.2],
                                          [0.0, 1.0, 0.0]], dtype=self.dtype)
    observation_locs_data = tf.constant([0.0, 1.0, 2.0], dtype=self.dtype)
    observation_scale_data = tf.constant(0.5, dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Normal(loc=observation_locs,
                                             scale=observation_scale),
                                  num_steps=5)

    self.run_test_sample_consistent_mean_variance(self.evaluate, model,
                                                  num_samples=100000,
                                                  rtol=0.03)

  def test_single_sequence_posterior_marginals(self):

    # In this test we have a 9-vertex graph with precisely one
    # 7-vertex path from vertex 0 to vertex 8.
    # The hidden Markov model is a random walk on this
    # graph where the only observations are
    # "observed at 0", "observed in {1, 2, ..., 7}",
    # "observed at 8".
    # The purpose of this test is to ensure that transition
    # and observation matrices with many log probabilities
    # equal to -infinity, and where the result contains many
    # -infinities, are handled correctly.

    initial_prob = tf.constant(np.ones(9) / 9.0, dtype=self.dtype)
    edges = [(0, 1), (1, 2), (2, 3), (3, 4),
             (4, 6), (2, 5), (5, 6), (6, 7),
             (6, 8)]
    transition_matrix = np.zeros((9, 9))
    for (i, j) in edges:
      transition_matrix[i, j] = 1.
      transition_matrix[j, i] = 1.
    transition_matrix = tf.constant(
        transition_matrix / np.sum(transition_matrix, axis=1, keepdims=True),
        dtype=self.dtype)
    observation_probs = tf.constant(
        np.block([[1, 0, 0],
                  [np.zeros((7, 1)), np.ones((7, 1)), np.zeros((7, 1))],
                  [0, 0, 1]]),
        dtype=self.dtype)

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=7)

    observations = [0, 1, 1, 1, 1, 1, 2]

    probs = self.evaluate(
        model.posterior_marginals(observations).probs_parameter())
    expected_probs = np.eye(9)[[0, 1, 2, 3, 4, 6, 8]]

    self.assertAllClose(probs, expected_probs, rtol=1e-4, atol=0.0)

  @parameterized.parameters(
      (3, 2, 1, 0),
      (1, 2, 3, 0),
      (1, 0, 2, 3))
  def test_posterior_marginals_high_rank(self, rank_o, rank_t, rank_i, rank_s):
    def increase_rank(n, x):
      # By choosing prime number dimensions we make it less
      # likely that a test will pass for accidental reasons.
      primes = [3, 5, 7]
      for i in range(n):
        x = primes[i] * [x]
      return x

    observation_locs_data = tf.identity(
        increase_rank(rank_o, tf.eye(4, dtype=self.dtype)))
    observation_scales_data = tf.constant(
        [0.25, 0.25, 0.25, 0.25],
        dtype=self.dtype)
    transition_matrix_data = tf.constant(
        increase_rank(rank_t, [[0.8, 0.1, 0.1, 0.0],
                               [0.1, 0.8, 0.0, 0.1],
                               [0.1, 0.0, 0.8, 0.1],
                               [0.0, 0.1, 0.1, 0.8]]),
        dtype=self.dtype)
    initial_prob_data = tf.constant(
        increase_rank(rank_i, [0.25, 0.25, 0.25, 0.25]),
        dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scales) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scales_data])

    observations = tf.constant(
        increase_rank(rank_s,
                      [[[0.91, 0.11], [0.21, 0.09]],
                       [[0.11, 0.97], [0.12, 0.08]],
                       [[0.01, 0.12], [0.92, 0.11]],
                       [[0.02, 0.11], [0.77, 0.11]],
                       [[0.81, 0.15], [0.21, 0.03]],
                       [[0.01, 0.13], [0.23, 0.91]],
                       [[0.11, 0.12], [0.23, 0.79]],
                       [[0.13, 0.11], [0.91, 0.29]]]),
        dtype=self.dtype)

    observation_distribution = tfp.distributions.TransformedDistribution(
        tfd.MultivariateNormalDiag(observation_locs,
                                   scale_diag=observation_scales),
        tfp.bijectors.Reshape((2, 2)))

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob),
        tfd.Categorical(probs=transition_matrix),
        observation_distribution,
        num_steps=8,
        validate_args=True)

    inferred_probs = self.evaluate(
        model.posterior_marginals(observations).probs_parameter())
    rank_e = max(rank_o, rank_t, rank_i, rank_s)
    expected_probs = increase_rank(rank_e,
                                   [[0.99994, 0.00000, 0.00006, 0.00000],
                                    [0.45137, 0.01888, 0.52975, 0.00000],
                                    [0.00317, 0.00002, 0.98112, 0.01570],
                                    [0.00000, 0.00001, 0.99998, 0.00001],
                                    [0.00495, 0.00001, 0.94214, 0.05289],
                                    [0.00000, 0.00083, 0.00414, 0.99503],
                                    [0.00000, 0.00000, 0.00016, 0.99984],
                                    [0.00000, 0.00000, 0.99960, 0.00039]])
    self.assertAllClose(inferred_probs, expected_probs, rtol=0., atol=1e-4)

  def test_posterior_mode_basic_example(self):
    observation_locs_data = tf.constant([0.0, 1.0, 2.0, 3.0],
                                        dtype=self.dtype)
    observation_scale_data = tf.constant(0.25, dtype=self.dtype)

    transition_matrix_data = tf.constant([[0.9, 0.1, 0.0, 0.0],
                                          [0.1, 0.8, 0.1, 0.0],
                                          [0.0, 0.1, 0.8, 0.1],
                                          [0.0, 0.0, 0.1, 0.9]],
                                         dtype=self.dtype)
    initial_prob_data = tf.constant([0.25, 0.25, 0.25, 0.25],
                                    dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scale) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scale_data])

    observations = tf.constant([0.1, 0.2, 0.3, 0.4, 0.5,
                                3.0, 2.9, 2.8, 2.7, 2.6],
                               dtype=self.dtype)

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob),
        tfd.Categorical(probs=transition_matrix),
        tfd.Normal(observation_locs,
                   scale=observation_scale),
        num_steps=10,
        validate_args=True)

    inferred_states = model.posterior_mode(observations)
    expected_states = [0, 0, 0, 0, 1, 2, 3, 3, 3, 3]
    self.assertAllEqual(inferred_states, expected_states)

  @parameterized.parameters(
      (3, 2, 1, 0),
      (1, 2, 3, 0),
      (1, 0, 2, 3))
  def test_posterior_mode_high_rank(self, rank_o, rank_t, rank_i, rank_s):
    def increase_rank(n, x):
      # By choosing prime number dimensions we make it less
      # likely that a test will pass for accidental reasons.
      primes = [3, 5, 7]
      for i in range(n):
        x = primes[i] * [x]
      return x

    observation_locs_data = tf.constant(increase_rank(rank_o,
                                                      [[1.0, 0.0, 0.0, 0.0],
                                                       [0.0, 1.0, 0.0, 0.0],
                                                       [0.0, 0.0, 1.0, 0.0],
                                                       [0.0, 0.0, 0.0, 1.0]]),
                                        dtype=self.dtype)
    observation_scales_data = tf.constant(
        [0.25, 0.25, 0.25, 0.25],
        dtype=self.dtype)
    transition_matrix_data = tf.constant(
        increase_rank(rank_t, [[0.8, 0.1, 0.1, 0.0],
                               [0.1, 0.8, 0.0, 0.1],
                               [0.1, 0.0, 0.8, 0.1],
                               [0.0, 0.1, 0.1, 0.8]]),
        dtype=self.dtype)
    initial_prob_data = tf.constant(
        increase_rank(rank_i, [0.25, 0.25, 0.25, 0.25]),
        dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs, observation_scales) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data, observation_scales_data])

    observations = tf.constant(
        increase_rank(rank_s,
                      [[[0.91, 0.11], [0.21, 0.09]],
                       [[0.11, 0.97], [0.12, 0.08]],
                       [[0.01, 0.12], [0.92, 0.11]],
                       [[0.02, 0.11], [0.77, 0.11]],
                       [[0.81, 0.15], [0.21, 0.03]],
                       [[0.01, 0.13], [0.23, 0.91]],
                       [[0.11, 0.12], [0.23, 0.79]],
                       [[0.13, 0.11], [0.91, 0.29]]]),
        dtype=self.dtype)

    observation_distribution = tfp.distributions.TransformedDistribution(
        tfd.MultivariateNormalDiag(observation_locs,
                                   scale_diag=observation_scales),
        tfp.bijectors.Reshape((2, 2)))

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob),
        tfd.Categorical(probs=transition_matrix),
        observation_distribution,
        num_steps=8,
        validate_args=True)

    inferred_states = model.posterior_mode(observations)
    rank_e = max(rank_o, rank_t, rank_i, rank_s)
    expected_states = increase_rank(rank_e, [0, 2, 2, 2, 2, 3, 3, 2])
    self.assertAllEqual(inferred_states, expected_states)

  def test_posterior_mode_high_rank_batch(self):
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]],
                                         dtype=self.dtype)
    transition_matrix_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]],
                                         dtype=self.dtype)
    initial_prob_data = tf.constant([0.5, 0.5],
                                    dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    observations = tf.constant(2*[3*[[5*[0], 5*[1]]]])

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob),
        tfd.Categorical(probs=transition_matrix),
        tfd.Categorical(probs=observation_probs),
        num_steps=5)

    inferred_states = model.posterior_mode(observations)
    expected_states = 2*[3*[[5*[0], 5*[1]]]]
    self.assertAllEqual(inferred_states, expected_states)

  # Check that the Viterbi algorithm is invariant under permutations of the
  # names of the observations of the HMM (when there is a unique most
  # likely sequence of hidden states).
  def test_posterior_mode_invariance_observations(self):
    observation_probs_data = tf.constant([[0.09, 0.48, 0.52, 0.11],
                                          [0.31, 0.21, 0.21, 0.27]],
                                         dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.90, 0.10],
                                          [0.30, 0.70]],
                                         dtype=self.dtype)
    initial_prob_data = tf.constant([0.65, 0.35],
                                    dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    permutations = tf.identity(np.array([np.random.permutation(4)
                                         for _ in range(8)]))
    inverse_permutations = tf.argsort(permutations)

    observation_probs_permuted = tf.transpose(
        a=tf.gather(tf.transpose(a=observation_probs),
                    inverse_permutations),
        perm=[0, 2, 1])

    observations = tf.constant([1, 0, 3, 1, 3, 0, 2, 1, 2, 1, 3, 0, 0, 1, 1, 2])
    observations_permuted = tf.transpose(
        a=tf.gather(tf.transpose(a=permutations)[..., tf.newaxis],
                    observations,
                    batch_dims=observations.shape.ndims-1)[..., 0])

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob),
        tfd.Categorical(probs=transition_matrix),
        tfd.Categorical(probs=observation_probs_permuted),
        num_steps=16)

    inferred_states = model.posterior_mode(observations_permuted)
    expected_states = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]
    self.assertAllEqual(inferred_states, 8*[expected_states])

  # Check that the Viterbi algorithm is invariant under permutations of the
  # names of the hidden states of the HMM (when there is a unique most
  # likely sequence of hidden states).
  def test_posterior_mode_invariance_states(self):
    observation_probs_data = tf.constant([[0.12, 0.48, 0.5, 0.1],
                                          [0.4, 0.1, 0.5, 0.0],
                                          [0.1, 0.2, 0.3, 0.4]],
                                         dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.21, 0.49, 0.3],
                                          [0.18, 0.12, 0.7],
                                          [0.75, 0.15, 0.1]],
                                         dtype=self.dtype)
    initial_prob_data = tf.constant([0.8, 0.13, 0.07],
                                    dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    permutations = tf.identity(np.array([np.random.permutation(3)
                                         for _ in range(8)]))
    inverse_permutations = tf.argsort(permutations)

    initial_prob_permuted = tf.gather(initial_prob, inverse_permutations)

    # Permute rows of observation matrix
    observation_probs_permuted = tf.gather(observation_probs,
                                           inverse_permutations)

    # Permute both rows and columns of transition matrix
    transition_matrix_permuted = tf.transpose(
        a=tf.gather(tf.transpose(a=transition_matrix),
                    inverse_permutations),
        perm=[0, 2, 1])
    transition_matrix_permuted = tf.compat.v1.batch_gather(
        transition_matrix_permuted,
        inverse_permutations)

    observations = tf.constant([1, 0, 3, 1, 3, 0, 2, 1, 2, 1, 3, 0, 0, 1, 1, 2])

    model = tfd.HiddenMarkovModel(
        tfd.Categorical(probs=initial_prob_permuted),
        tfd.Categorical(probs=transition_matrix_permuted),
        tfd.Categorical(probs=observation_probs_permuted),
        num_steps=16)

    inferred_states = model.posterior_mode(observations)
    expected_states = [0, 1, 2, 0, 2, 1, 2, 0, 2, 0, 2, 0, 1, 2, 0, 1]
    expected_states_permuted = tf.transpose(
        a=tf.compat.v1.batch_gather(tf.expand_dims(tf.transpose(a=permutations),
                                                   axis=-1),
                                    expected_states)[..., 0])
    self.assertAllEqual(inferred_states, expected_states_permuted)

  def test_posterior_mode_missing_continuous_observations(self):
    initial_prob_data = tf.constant([0.5, 0.5], dtype=self.dtype)
    transition_matrix_data = tf.constant([[[0.6, 0.4],
                                           [0.6, 0.4]],
                                          [[0.4, 0.6],
                                           [0.4, 0.6]]], dtype=self.dtype)
    observation_locs_data = tf.constant([[0.0, 0.0],
                                         [10.0, 10.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_locs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_locs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.MultivariateNormalDiag(
                                      loc=observation_locs),
                                  num_steps=3)

    observations = tf.constant([[0.0, 0.0],
                                [0.0, 0.0],
                                [10.0, 10.0]], dtype=self.dtype)

    # We test two different transition matrices as well as two
    # different masks.
    # As a result we have a 2x2 tensor of sequences of states
    # returned by `posterior_mode`.
    x = model.posterior_mode(observations, mask=[[[False, True, False]],
                                                 [[False, False, False]]])

    self.assertAllEqual(x, [[[0, 0, 1], [0, 1, 1]],
                            [[0, 0, 1], [0, 0, 1]]])

  def test_posterior_mode_missing_discrete_observations(self):
    initial_prob = tf.constant([1.0, 0.0, 0.0, 0.0], dtype=self.dtype)

    # This test uses a model with a random walk that can make a change of
    # of -1, 0 or +1 at each step.
    transition_data = (0.5 * np.diag(np.ones(4)) +
                       0.25*np.diag(np.ones(3), -1) +
                       0.25*np.diag(np.ones(3), 1))
    transition_data[0, 0] += 0.25
    transition_data[3, 3] += 0.25
    transition_matrix = tf.constant(transition_data, dtype=self.dtype)

    # Observations of the random walk are unreliable and give the
    # correct position with probability `0.25 + 0.75 * reliability`
    def observation_fn(reliability):
      return np.array(reliability * np.diag(np.ones(4)) +
                      (1 - reliability) * 0.25 * np.ones((4, 4)))

    observation_data = np.array(
        [observation_fn(reliability)
         for reliability in [0.993, 0.994, 0.995, 0.996]])
    observation_probs = tf.constant(observation_data, dtype=self.dtype)

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=7)

    observations = tf.constant([0, 1, 2, 3, 2, 1, 0])
    mask = tf.constant([False, True, True, False, True, True, False])

    inferred_states = model.posterior_mode(observations, mask)

    # This example has been tuned so that there are two local maxima in the
    # space of paths.
    # As the `reliability` parameter increases, the mode switches from one of
    # the two paths to the other.
    expected_states = [[0, 0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0, 0],
                       [0, 1, 2, 3, 2, 1, 0],
                       [0, 1, 2, 3, 2, 1, 0]]
    self.assertAllEqual(inferred_states, expected_states)

  def test_posterior_marginals_missing_observations(self):
    initial_prob = tf.constant([1., 0., 0., 0.], dtype=self.dtype)

    # This test uses a model with a random walk that can make a change of
    # of -1, 0 or +1 at each step.
    transition_data = [[0.75, 0.25, 0., 0.],
                       [0.25, 0.5, 0.25, 0.],
                       [0., 0.25, 0.5, 0.25],
                       [0.0, 0.0, 0.25, 0.75]]
    transition_matrix = tf.constant(transition_data, dtype=self.dtype)

    observation_data = np.array(np.eye(4))
    observation_probs = tf.constant(observation_data, dtype=self.dtype)

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=7)

    observations = tf.constant([0, 1, 2, 3, 2, 1, 0])
    mask = tf.constant([False, True, True, True, True, True, False])

    marginals = self.evaluate(
        model.posterior_marginals(observations, mask).probs_parameter())
    expected_marginals = [[1., 0., 0., 0.],
                          [21./26, 5./26, 0., 0.],
                          [105./143, 35./143, 3./143, 0.],
                          [1225./1716, 147./572, 49./1716, 1./1716],
                          [105./143, 35./143, 3./143, 0.],
                          [21./26, 5./26, 0., 0.],
                          [1., 0., 0., 0.]]
    self.assertAllClose(marginals, expected_marginals)

  def test_posterior_mode_edge_case_no_transitions(self):
    # Test all eight combinations of a single state that is
    # 1. unmasked/masked
    # 2. observed at state 0/state 1
    # 3. more likely started at state 0/state 1
    initial_prob_data = tf.constant([[0.9, 0.1], [0.1, 0.9]], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=1)

    inferred_state = model.posterior_mode(
        observations=[[[0]], [[1]]],
        mask=[[[[True]]], [[[False]]]])

    expected_state = [[[[0], [1]], [[0], [1]]],
                      [[[0], [0]], [[1], [1]]]]

    self.assertAllEqual(inferred_state, expected_state)

  def test_posterior_marginals_edge_case_no_transitions(self):
    # Test all eight combinations of a single state that is
    # 1. unmasked/masked
    # 2. observed at state 0/state 1
    # 3. more likely started at state 0/state 1
    initial_prob_data = tf.constant([[0.9, 0.1], [0.1, 0.9]], dtype=self.dtype)
    transition_matrix_data = tf.constant([[0.5, 0.5],
                                          [0.5, 0.5]], dtype=self.dtype)
    observation_probs_data = tf.constant([[1.0, 0.0],
                                          [0.0, 1.0]], dtype=self.dtype)

    (initial_prob, transition_matrix,
     observation_probs) = self.make_placeholders([
         initial_prob_data, transition_matrix_data,
         observation_probs_data])

    model = tfd.HiddenMarkovModel(tfd.Categorical(probs=initial_prob),
                                  tfd.Categorical(probs=transition_matrix),
                                  tfd.Categorical(probs=observation_probs),
                                  num_steps=1)

    inferred_marginals = self.evaluate(
        model.posterior_marginals(
            observations=[[[0]], [[1]]],
            mask=[[[[True]]], [[[False]]]]).probs_parameter())

    # Result is a [2,2,2] batch of sequences of length 1 of
    # [2]-vectors of probabilities.
    expected_marginals = [[[[[0.9, 0.1]],
                            [[0.1, 0.9]]],
                           [[[0.9, 0.1]],
                            [[0.1, 0.9]]]],
                          [[[[1., 0.]],
                            [[1., 0.]]],
                           [[[0., 1.]],
                            [[0., 1.]]]]]

    self.assertAllClose(inferred_marginals, expected_marginals)


class HiddenMarkovModelTestFloat32(_HiddenMarkovModelTest):
  dtype = tf.float32


class HiddenMarkovModelTestFloat64(_HiddenMarkovModelTest):
  dtype = tf.float64

del _HiddenMarkovModelTest

if __name__ == "__main__":
  tf.test.main()
