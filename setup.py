from setuptools import setup, find_packages

setup(name='juju-lxc',
      version="0.0.3",
      classifiers=[
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Operating System :: OS Independent'],
      author='Kapil Thangavelu',
      author_email='kapil.foss@gmail.com',
      description="An alternate lxc container integration with juju",
      long_description=open("readme.rst").read(),
      url='http://github/kapilt/juju-docean',
      license='BSD',
      packages=find_packages(),
      install_requires=["PyYAML", "dop"],
      entry_points={
          "console_scripts": [
              'jlxc-add = juju_lxc.add:main',
              'jlxc-destroy = juju_lxc.destroy:main']},
      )
