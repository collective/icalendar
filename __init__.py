import os
import sys

# this allows the iCalendar package to be installed as a Zope product.
# It will add the src directory to the PYTHONPATH.
# Note that this strictly optional, just makes deployment with
# Zope more easy.
product_dir, filename = os.path.split(__file__)
src_path = os.path.join(product_dir, 'src')
sys.path.append(src_path)

def initialize(context):
    pass
