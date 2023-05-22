=============================
Visulization
=============================

Enable TensorBoard when creating the Benchmark first.

.. code-block:: python

    bench = Benchmark(SystemUnderTest, 
                      num_workers=1, 
                      enable_tensorboard=True)

Start TensorBoard at http://localhost:6006/

.. code-block:: bash

    # Install TensorBoard and PyTorch(providing the easy-to-use SummaryWriter):
    pip install tensorboard pytorch
    # Start TensorBoard to visualize realtime qps and latency results:
    tensorboard --logdir runs
