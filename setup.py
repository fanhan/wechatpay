# -*- coding:utf-8 -*-

import sys
sys.path.append('./src')

from distutils.core import setup
from wechatpay import __version__

setup(name='wechatpay',
      version=__version__,
      description='A relative to wechat payment project',
      long_description=open("README.md").read(),
      author='leavesfan',
      author_email='leavesfan@gmail.com',
      packages=['wechatpay'],
      package_dir={'wechatpay': 'src/wechatpay'},
      package_data={'wechatpay': ['payment']},
      license="Public domain",
      platforms=["any"],
      url='https://github.com/fanhan/wechatpay')
