import pathlib

from tma.core import DataAnalyzer
from pathlib import Path


def main():
    dir_path = pathlib.Path.cwd()
    filepath_1 = str(Path(dir_path, 'files/VF03_H1O.cur'))
    filepath_2 = str(Path(dir_path, 'files/VF03_L1.clw'))
    filepath_3 = str(Path(dir_path, 'files/VF03_L2.clw'))
    analyzer = DataAnalyzer([filepath_1, filepath_2, filepath_3])


if __name__ == "__main__":
    main()
