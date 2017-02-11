import numpy as np
import tensorflow as tf

from tensor_train import TensorTrain

def determinant(kron_a):
  """Computes the determinant of a given matrix, factorized into
  a Kronecker product of square matrices.
  
  Note, that this method can suffer from overflow.

  Args:
    kron_a: `TensorTrain` object containing a matrix of size N x N, 
    factorized into a Kronecker product of square matrices (all 
    tt-ranks are 1 and all tt-cores are square). 
  
  Returns:
    Number, the determinant of the given matrix

  Raises:
    ValueError if the tt-cores of the provided matrix are not square,
    or the tt-ranks are not 1
  """
  if not _is_kron(kron_a):
    raise ValueError('The argument should be a Kronecker product (tt-ranks should be 1)')

  cores = kron_a.tt_cores
  det, pows = 1, 1
  for core_idx in range(kron_a.ndims()):
    core = kron_a.tt_cores[core_idx]
    if core.get_shape()[1] != core.get_shape()[2]:
      raise ValueError('The argument should be a Kronecker product of square matrices' 
                      '(tt-cores must be square)')
    pows *= core.get_shape()[1].value
  for core_idx in range(kron_a.ndims()):
    core = cores[core_idx]
    det *= tf.pow(tf.matrix_determinant(core[0, :, :, 0]), pows / core.get_shape()[1].value)
  return det


def log_determinant(kron_a):
  """Computes the log-determinant of a given matrix, factorized into
  a Kronecker product of square matrices.

  Args:
    kron_a: `TensorTrain` object containing a matrix of size N x N, 
    factorized into a Kronecker product of square matrices (all 
    tt-ranks are 1 and all tt-cores are square). All the cores
    must have positive determinants
  
  Returns:
    Number, the log-determinant of the given matrix

  Raises:
    ValueError if the cores are not square, or there determinants
    are not positive
  """
  if not _is_kron(kron_a):
    raise ValueError('The argument should be a Kronecker product (tt-ranks should be 1)')
  
  pows = 1
  for core_idx in range(kron_a.ndims()):
    core = kron_a.tt_cores[core_idx]
    if core.get_shape()[1] != core.get_shape()[2]:
      raise ValueError('The argument should be a Kronecker product of square matrices' 
                      '(tt-cores must be square)')
    pows *= core.get_shape()[1].value
                                                          
  logdet = 0
  for core_idx in range(kron_a.ndims()):
    core = kron_a.tt_cores[core_idx]
    logdet += tf.log(tf.matrix_determinant(core[0, :, :, 0])) * (pows / core.get_shape()[1].value)
  
  #TODO: raise error, if nan 
  return logdet

def inv(kron_a):
  """Computes the inverse of a given matrix, factorized into
  a Kronecker-product of square matrices.

  Args:
    kron_a: `TensorTrain` object containing a matrix of size N x N, 
    factorized into a Kronecker product of square matrices (all 
    tt-ranks are 1 and all tt-cores are square). All the cores
    must be invertable

  Returns:
    `TensorTrain` object, containing a TT-matrix of size N x N    
  """
  if not _is_kron(kron_a):
    raise ValueError('The argument should be a Kronecker product (tt-ranks should be 1)')

  inv_cores = []
  for core_idx in range(kron_a.ndims()):
    core = kron_a.tt_cores[core_idx]
    if core.get_shape()[1] != core.get_shape()[2]:
      raise ValueError('The argument should be a Kronecker product of square matrices' 
                      '(tt-cores must be square)')
 
    core_inv = tf.matrix_inverse(core[0, :, :, 0])
    inv_cores.append(tf.expand_dims(tf.expand_dims(core_inv, 0), -1))

  res_ranks = tf.TensorShape([1] * (kron_a.ndims() + 1))
  res_shape = kron_a.get_raw_shape()
  return TensorTrain(inv_cores, res_shape, res_ranks) 

def cholesky(kron_a):
  """Computes the Cholesky decomposition of a given matrix, factorized 
  into a Kronecker-product of symmetric positive-definite square matrices.

  Args:
    kron_a: `TensorTrain` object containing a matrix of size N x N, 
    factorized into a Kronecker product of square matrices (all 
    tt-ranks are 1 and all tt-cores are square). All the cores
    must be symmetric positive-definite

  Returns:
    `TensorTrain` object, containing a TT-matrix of size N x N    
  """
  if not _is_kron(kron_a):
    raise ValueError('The argument should be a Kronecker product')

  cho_cores = []
  for core_idx in range(kron_a.ndims()):
    core = kron_a.tt_cores[core_idx]
    if core.get_shape()[1] != core.get_shape()[2]:
      raise ValueError('The argument should be a Kronecker product of square matrices' 
                      '(tt-cores must be square)')
    core_cho = tf.cholesky(core[0, :, :, 0])
    cho_cores.append(tf.expand_dims(tf.expand_dims(core_cho, 0), -1))

  res_ranks = tf.TensorShape([1] * (kron_a.ndims() + 1))
  res_shape = kron_a.get_raw_shape()
  return TensorTrain(cho_cores, res_shape, res_ranks) 

def _is_kron(tt_a):
  """Returns True if the argument is a Kronecker product matrix.

  Args:
    tt_a: `TensorTrain` object

  Returns:
    bool
  """
  if tt_a.is_tt_matrix():
    return max(tt_a.get_tt_ranks()) == 1
  return False    

