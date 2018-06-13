import os
import glob


def find_mtl_in_product_dir(productdir):
    pattern = os.path.join(productdir, '*_MTL.txt')
    mtlfiles = glob.glob(pattern)
    if len(mtlfiles) != 1:
        raise RuntimeError('Expecting exactly one MTL file in product dir. Found {} with pattern \'{}\'.'.format(len(mtlfiles), pattern))
    return mtlfiles[0]
