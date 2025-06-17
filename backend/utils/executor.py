import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def execute_and_plot(code: str, df, output_path: str) -> str:
    """
    Executes `code` in a context:
      - df: your pre-cleaned pandas DataFrame
      - plt: matplotlib.pyplot
      - output_path: where to save the PNG
    """
    ctx = {'df': df, 'plt': plt, 'output_path': output_path}
    exec(code, {}, ctx)

    if not os.path.exists(output_path):
        raise RuntimeError("Plot code ran but did not produce a file")
    return output_path
