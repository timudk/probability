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
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

# Dependency imports
import numpy as np
import tensorflow.compat.v1 as tf1
import tensorflow.compat.v2 as tf
import tensorflow_probability as tfp

from tensorflow_probability.python.internal import tensorshape_util
from tensorflow.python.framework import test_util  # pylint: disable=g-direct-tensorflow-import,g-import-not-at-top


tfd = tfp.distributions


class TupleDistribution(tfd.Distribution):

  def __init__(self):
    super(TupleDistribution, self).__init__(
        dtype=None, reparameterization_type=None,
        validate_args=False, allow_nan_stats=False)

  @property
  def name(self):
    return 'TupleDistribution'

  @property
  def dtype(self):
    return (tf.float16, None, tf.int32)

  @property
  def batch_shape(self):
    return (tf.TensorShape(None), None, tf.TensorShape([None, 2]))

  @property
  def event_shape(self):
    return (None, tf.TensorShape([3, None]), tf.TensorShape(None))


class DictDistribution(tfd.Distribution):

  def __init__(self):
    super(DictDistribution, self).__init__(
        dtype=None, reparameterization_type=None,
        validate_args=False, allow_nan_stats=False)

  @property
  def name(self):
    return 'DictDistribution'

  @property
  def dtype(self):
    return dict(a=tf.float16, b=None, c=tf.int32)

  @property
  def batch_shape(self):
    return dict(a=tf.TensorShape(None), b=None, c=tf.TensorShape([None, 2]))

  @property
  def event_shape(self):
    return dict(a=None, b=tf.TensorShape([3, None]), c=tf.TensorShape(None))


class NamedTupleDistribution(tfd.Distribution):

  class MyType(collections.namedtuple('MyType', 'a b c')):
    __slots__ = ()

  def __init__(self):
    super(NamedTupleDistribution, self).__init__(
        dtype=None, reparameterization_type=None,
        validate_args=False, allow_nan_stats=False)

  @property
  def name(self):
    return 'NamedTupleDistribution'

  @property
  def dtype(self):
    return self.MyType(a=tf.float16, b=None, c=tf.int32)

  @property
  def batch_shape(self):
    return self.MyType(
        a=tf.TensorShape(None), b=None, c=tf.TensorShape([None, 2]))

  @property
  def event_shape(self):
    return self.MyType(
        a=None, b=tf.TensorShape([3, None]), c=tf.TensorShape(None))


@test_util.run_all_in_graph_and_eager_modes
class DistributionStrReprTest(tf.test.TestCase):

  def testStrWorksCorrectlyScalar(self):
    normal = tfd.Normal(loc=np.float16(0), scale=1)
    self.assertEqual(
        str(normal),
        'tfp.distributions.Normal('
        '"Normal", '
        'batch_shape=[], '
        'event_shape=[], '
        'dtype=float16)')

    chi2 = tfd.Chi2(df=np.float32([1., 2.]), name='silly')
    self.assertEqual(
        str(chi2),
        'tfp.distributions.Chi2('
        '"silly", '  # What a silly name that is!
        'batch_shape=[2], '
        'event_shape=[], '
        'dtype=float32)')

    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    if tf.executing_eagerly():
      return

    exp = tfd.Exponential(
        rate=tf1.placeholder_with_default(input=1., shape=None))
    self.assertEqual(
        str(exp),
        'tfp.distributions.Exponential("Exponential", '
        # No batch shape.
        'event_shape=[], '
        'dtype=float32)')

  def testStrWorksCorrectlyMultivariate(self):
    mvn_static = tfd.MultivariateNormalDiag(
        loc=np.zeros([2, 2]), name='MVN')
    self.assertEqual(
        str(mvn_static),
        'tfp.distributions.MultivariateNormalDiag('
        '"MVN", '
        'batch_shape=[2], '
        'event_shape=[2], '
        'dtype=float64)')

    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    if tf.executing_eagerly():
      return

    mvn_dynamic = tfd.MultivariateNormalDiag(
        loc=tf1.placeholder_with_default(
            input=np.ones((3, 3), dtype=np.float32), shape=[None, 3]),
        name='MVN2')
    self.assertEqual(
        str(mvn_dynamic),
        'tfp.distributions.MultivariateNormalDiag('
        '"MVN2", '
        'batch_shape=[?], '  # Partially known.
        'event_shape=[3], '
        'dtype=float32)')

  def testReprWorksCorrectlyScalar(self):
    normal = tfd.Normal(loc=np.float16(0), scale=np.float16(1))
    self.assertEqual(
        repr(normal),
        '<tfp.distributions.Normal'
        ' \'Normal\''
        ' batch_shape=[]'
        ' event_shape=[]'
        ' dtype=float16>')

    chi2 = tfd.Chi2(df=np.float32([1., 2.]), name='silly')
    self.assertEqual(
        repr(chi2),
        '<tfp.distributions.Chi2'
        ' \'silly\''  # What a silly name that is!
        ' batch_shape=[2]'
        ' event_shape=[]'
        ' dtype=float32>')

    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    if tf.executing_eagerly():
      return

    exp = tfd.Exponential(
        rate=tf1.placeholder_with_default(input=1., shape=None))
    self.assertEqual(
        repr(exp),
        '<tfp.distributions.Exponential'
        ' \'Exponential\''
        ' batch_shape=?'
        ' event_shape=[]'
        ' dtype=float32>')

  def testReprWorksCorrectlyMultivariate(self):
    mvn_static = tfd.MultivariateNormalDiag(
        loc=np.zeros([2, 2]), name='MVN')
    self.assertEqual(
        repr(mvn_static),
        '<tfp.distributions.MultivariateNormalDiag'
        ' \'MVN\''
        ' batch_shape=[2]'
        ' event_shape=[2]'
        ' dtype=float64>')

    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    if tf.executing_eagerly():
      return

    mvn_dynamic = tfd.MultivariateNormalDiag(
        loc=tf1.placeholder_with_default(
            input=np.ones((3, 3), dtype=np.float32), shape=[None, 3]),
        name='MVN2')
    self.assertEqual(
        repr(mvn_dynamic),
        '<tfp.distributions.MultivariateNormalDiag'
        ' \'MVN2\''
        ' batch_shape=[?]'  # Partially known.
        ' event_shape=[3]'
        ' dtype=float32>')

  def testStrWorksCorrectlyTupleDistribution(self):
    self.assertEqual(
        str(TupleDistribution()),
        'tfp.distributions.TupleDistribution("TupleDistribution",'
        ' batch_shape=(?, ?, [?, 2]),'
        ' event_shape=(?, [3, ?], ?),'
        ' dtype=(float16, ?, int32))')

  def testReprWorksCorrectlyTupleDistribution(self):
    self.assertEqual(
        repr(TupleDistribution()),
        '<tfp.distributions.TupleDistribution \'TupleDistribution\''
        ' batch_shape=(?, ?, [?, 2])'
        ' event_shape=(?, [3, ?], ?)'
        ' dtype=(float16, ?, int32)>')

  def testStrWorksCorrectlyDictDistribution(self):
    self.assertEqual(
        str(DictDistribution()),
        'tfp.distributions.DictDistribution("DictDistribution",'
        ' batch_shape={a: ?, b: ?, c: [?, 2]},'
        ' event_shape={a: ?, b: [3, ?], c: ?},'
        ' dtype={a: float16, b: ?, c: int32})')

  def testReprWorksCorrectlyDictDistribution(self):
    self.assertEqual(
        repr(DictDistribution()),
        '<tfp.distributions.DictDistribution \'DictDistribution\''
        ' batch_shape={a: ?, b: ?, c: [?, 2]}'
        ' event_shape={a: ?, b: [3, ?], c: ?}'
        ' dtype={a: float16, b: ?, c: int32}>')

  def testStrWorksCorrectlyNamedTupleDistribution(self):
    self.assertEqual(
        str(NamedTupleDistribution()),
        'tfp.distributions.NamedTupleDistribution("NamedTupleDistribution",'
        ' batch_shape=MyType(a=?, b=?, c=[?, 2]),'
        ' event_shape=MyType(a=?, b=[3, ?], c=?),'
        ' dtype=MyType(a=float16, b=?, c=int32))')

  def testReprWorksCorrectlyNamedTupleDistribution(self):
    self.assertEqual(
        repr(NamedTupleDistribution()),
        '<tfp.distributions.NamedTupleDistribution \'NamedTupleDistribution\''
        ' batch_shape=MyType(a=?, b=?, c=[?, 2])'
        ' event_shape=MyType(a=?, b=[3, ?], c=?)'
        ' dtype=MyType(a=float16, b=?, c=int32)>')


@test_util.run_all_in_graph_and_eager_modes
class DistributionTest(tf.test.TestCase):

  def testParamShapesAndFromParams(self):
    classes = [
        tfd.Normal,
        tfd.Bernoulli,
        tfd.Beta,
        tfd.Chi2,
        tfd.Exponential,
        tfd.Gamma,
        tfd.InverseGamma,
        tfd.Laplace,
        tfd.StudentT,
        tfd.Uniform,
    ]

    sample_shapes = [(), (10,), (10, 20, 30)]
    for cls in classes:
      for sample_shape in sample_shapes:
        param_shapes = cls.param_shapes(sample_shape)
        params = dict([(name, tf.random.normal(shape))
                       for name, shape in param_shapes.items()])
        dist = cls(**params)
        self.assertAllEqual(sample_shape,
                            self.evaluate(tf.shape(input=dist.sample())))
        dist_copy = dist.copy()
        self.assertAllEqual(sample_shape,
                            self.evaluate(tf.shape(input=dist_copy.sample())))
        self.assertEqual(dist.parameters, dist_copy.parameters)

  def testCopyExtraArgs(self):
    # Note: we cannot easily test all distributions since each requires
    # different initialization arguments. We therefore spot test a few.
    normal = tfd.Normal(loc=1., scale=2., validate_args=True)
    self.assertEqual(normal.parameters, normal.copy().parameters)
    wishart = tfd.Wishart(df=2, scale=[[1., 2], [2, 5]], validate_args=True)
    self.assertEqual(wishart.parameters, wishart.copy().parameters)

  def testCopyOverride(self):
    normal = tfd.Normal(loc=1., scale=2., validate_args=True)
    unused_normal_copy = normal.copy(validate_args=False)
    base_params = normal.parameters.copy()
    copy_params = normal.copy(validate_args=False).parameters.copy()
    self.assertNotEqual(
        base_params.pop('validate_args'), copy_params.pop('validate_args'))
    self.assertEqual(base_params, copy_params)

  def testIsScalar(self):
    mu = 1.
    sigma = 2.

    normal = tfd.Normal(mu, sigma, validate_args=True)
    self.assertTrue(tf.get_static_value(normal.is_scalar_event()))
    self.assertTrue(tf.get_static_value(normal.is_scalar_batch()))

    normal = tfd.Normal([mu], [sigma], validate_args=True)
    self.assertTrue(tf.get_static_value(normal.is_scalar_event()))
    self.assertFalse(tf.get_static_value(normal.is_scalar_batch()))

    mvn = tfd.MultivariateNormalDiag([mu], [sigma], validate_args=True)
    self.assertFalse(tf.get_static_value(mvn.is_scalar_event()))
    self.assertTrue(tf.get_static_value(mvn.is_scalar_batch()))

    mvn = tfd.MultivariateNormalDiag([[mu]], [[sigma]], validate_args=True)
    self.assertFalse(tf.get_static_value(mvn.is_scalar_event()))
    self.assertFalse(tf.get_static_value(mvn.is_scalar_batch()))

    # We now test every codepath within the underlying is_scalar_helper
    # function.

    # Test case 1, 2.
    x = tf1.placeholder_with_default(input=1, shape=[])
    # None would fire an exception were it actually executed.
    self.assertTrue(normal._is_scalar_helper(x.shape, lambda: None))
    self.assertTrue(
        normal._is_scalar_helper(
            tf.TensorShape(None), lambda: tf.shape(input=x)))

    x = tf1.placeholder_with_default(input=[1], shape=[1])
    # None would fire an exception were it actually executed.
    self.assertFalse(normal._is_scalar_helper(x.shape, lambda: None))
    self.assertFalse(
        normal._is_scalar_helper(
            tf.TensorShape(None), lambda: tf.shape(input=x)))

    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    if tf.executing_eagerly():
      return

    # Test case 3.
    x = tf1.placeholder_with_default(input=1, shape=None)
    is_scalar = normal._is_scalar_helper(x.shape, lambda: tf.shape(input=x))
    self.assertTrue(self.evaluate(is_scalar))

    x = tf1.placeholder_with_default(input=[1], shape=None)
    is_scalar = normal._is_scalar_helper(x.shape, lambda: tf.shape(input=x))
    self.assertFalse(self.evaluate(is_scalar))

  def _GetFakeDistribution(self):
    class FakeDistribution(tfd.Distribution):
      """Fake Distribution for testing _set_sample_static_shape."""

      def __init__(self, batch_shape=None, event_shape=None):
        self._static_batch_shape = tf.TensorShape(batch_shape)
        self._static_event_shape = tf.TensorShape(event_shape)
        super(FakeDistribution, self).__init__(
            dtype=tf.float32,
            reparameterization_type=tfd.NOT_REPARAMETERIZED,
            validate_args=True,
            allow_nan_stats=True,
            name='DummyDistribution')

      def _batch_shape(self):
        return self._static_batch_shape

      def _event_shape(self):
        return self._static_event_shape

    return FakeDistribution

  def testSampleShapeHints(self):
    # In eager mode, all shapes are known, so these tests do not need to
    # execute.
    if tf.executing_eagerly():
      return

    fake_distribution = self._GetFakeDistribution()

    # Make a new session since we're playing with static shapes. [And below.]
    x = tf1.placeholder_with_default(
        input=np.ones((6, 7, 2, 3, 5), dtype=np.float32), shape=None)
    dist = fake_distribution(batch_shape=[2, 3], event_shape=[5])
    sample_shape = tf.convert_to_tensor(value=[6, 7], dtype=tf.int32)
    y = dist._set_sample_static_shape(x, sample_shape)
    # We use as_list since TensorShape comparison does not work correctly for
    # unknown values, ie, Dimension(None).
    self.assertAllEqual([6, 7, 2, 3, 5], tensorshape_util.as_list(y.shape))

    x = tf1.placeholder_with_default(
        input=np.ones((6, 7, 2, 3, 5), dtype=np.float32), shape=None)
    dist = fake_distribution(batch_shape=[None, 3], event_shape=[5])
    sample_shape = tf.convert_to_tensor(value=[6, 7], dtype=tf.int32)
    y = dist._set_sample_static_shape(x, sample_shape)
    self.assertAllEqual([6, 7, None, 3, 5], tensorshape_util.as_list(y.shape))

    x = tf1.placeholder_with_default(
        input=np.ones((6, 7, 2, 3, 5), dtype=np.float32), shape=None)
    dist = fake_distribution(batch_shape=[None, 3], event_shape=[None])
    sample_shape = tf.convert_to_tensor(value=[6, 7], dtype=tf.int32)
    y = dist._set_sample_static_shape(x, sample_shape)
    self.assertAllEqual([6, 7, None, 3, None],
                        tensorshape_util.as_list(y.shape))

    x = tf1.placeholder_with_default(
        input=np.ones((6, 7, 2, 3, 5), dtype=np.float32), shape=None)
    dist = fake_distribution(batch_shape=None, event_shape=None)
    sample_shape = tf.convert_to_tensor(value=[6, 7], dtype=tf.int32)
    y = dist._set_sample_static_shape(x, sample_shape)
    self.assertIsNone(tensorshape_util.rank(y.shape))

    x = tf1.placeholder_with_default(
        input=np.ones((6, 7, 2, 3, 5), dtype=np.float32), shape=None)
    dist = fake_distribution(batch_shape=[None, 3], event_shape=None)
    # There's no notion of partially known shapes in eager mode, so exit
    # early.
    sample_shape = tf.convert_to_tensor(value=[6, 7], dtype=tf.int32)
    y = dist._set_sample_static_shape(x, sample_shape)
    self.assertIsNone(tensorshape_util.rank(y.shape))

  def testNameScopeWorksCorrectly(self):
    x = tfd.Normal(loc=0., scale=1., name='x')
    x_duplicate = tfd.Normal(loc=0., scale=1., name='x')
    with tf.name_scope('y') as name:
      y = tfd.Bernoulli(logits=0., name=name)
    x_sample = x.sample(name='custom_sample')
    x_sample_duplicate = x.sample(name='custom_sample')
    x_log_prob = x.log_prob(0., name='custom_log_prob')
    x_duplicate_sample = x_duplicate.sample(name='custom_sample')

    self.assertStartsWith(x.name, 'x')
    self.assertStartsWith(y.name, 'y')

    # There's no notion of graph, hence the same name will be reused.
    # Tensors also do not have names in eager mode, so exit early.
    if tf.executing_eagerly():
      return
    self.assertStartsWith(x_sample.name, 'x_2/custom_sample')
    self.assertStartsWith(x_log_prob.name, 'x_4/custom_log_prob')

    self.assertStartsWith(x_duplicate.name, 'x_1')
    self.assertStartsWith(x_duplicate_sample.name, 'x_1_1/custom_sample')
    self.assertStartsWith(x_sample_duplicate.name, 'x_3/custom_sample')

  def testUnimplemtnedProbAndLogProbExceptions(self):
    class TerribleDistribution(tfd.Distribution):

      def __init__(self):
        super(TerribleDistribution, self).__init__(
            dtype=tf.float32,
            reparameterization_type=tfd.NOT_REPARAMETERIZED,
            validate_args=False,
            allow_nan_stats=False)

    terrible_distribution = TerribleDistribution()
    with self.assertRaisesRegexp(
        NotImplementedError, 'prob is not implemented'):
      terrible_distribution.prob(1.)
    with self.assertRaisesRegexp(
        NotImplementedError, 'log_prob is not implemented'):
      terrible_distribution.log_prob(1.)
    with self.assertRaisesRegexp(
        NotImplementedError, 'cdf is not implemented'):
      terrible_distribution.cdf(1.)
    with self.assertRaisesRegexp(
        NotImplementedError, 'log_cdf is not implemented'):
      terrible_distribution.log_cdf(1.)

  def testNotIterable(self):
    normal = tfd.Normal(loc=0., scale=1.)
    with self.assertRaisesRegexp(
        TypeError,
        '\'Normal\' object is not iterable'
    ):
      list(normal)


class Dummy(tfd.Distribution):

  # To ensure no code is keying on the unspecial name 'self', we use 'me'.
  def __init__(me, arg1, arg2, arg3=None, **named):  # pylint: disable=no-self-argument
    super(Dummy, me).__init__(
        dtype=tf.float32,
        reparameterization_type=tfd.NOT_REPARAMETERIZED,
        validate_args=False,
        allow_nan_stats=False)
    me._mean_ = tf.convert_to_tensor(value=arg1 + arg2)

  def _mean(self):
    return self._mean_


class ParametersTest(tf.test.TestCase):

  def testParameters(self):
    d = Dummy(1., arg2=2.)
    actual_d_parameters = d.parameters
    self.assertEqual({'arg1': 1., 'arg2': 2., 'arg3': None, 'named': {}},
                     actual_d_parameters)
    self.assertEqual(actual_d_parameters, d.parameters)

  @test_util.run_in_graph_and_eager_modes(assert_no_eager_garbage=True)
  def testNoSelfRefs(self):
    d = Dummy(1., arg2=2.)
    self.assertAllEqual(1. + 2., self.evaluate(d.mean()))

  def testTfFunction(self):
    if not tf.executing_eagerly(): return
    @tf.function
    def normal_differential_entropy(scale):
      return tfd.Normal(0., scale).entropy()
    scale = 0.25
    self.assertNear(0.5 * np.log(2. * np.pi * np.e * scale**2.),
                    normal_differential_entropy(scale).numpy(),
                    err=1e-5)


@test_util.run_all_in_graph_and_eager_modes
class TfModuleTest(tf.test.TestCase):

  def test_variable_tracking_works(self):
    scale = tf.Variable(1.)
    normal = tfd.Normal(loc=0, scale=scale, validate_args=True)
    self.assertIsInstance(normal, tf.Module)
    self.assertEqual((scale,), normal.trainable_variables)

  def test_gradient(self):
    scale = tf.Variable(1.)
    normal = tfd.Normal(loc=0, scale=scale, validate_args=True)
    self.assertEqual((scale,), normal.trainable_variables)
    with tf.GradientTape() as tape:
      loss = -normal.log_prob(0.)
    g = tape.gradient(loss, normal.trainable_variables)
    self.evaluate(tf1.global_variables_initializer())
    self.assertEqual((1.,), self.evaluate(g))


if __name__ == '__main__':
  tf.test.main()
