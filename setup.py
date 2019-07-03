#!/usr/bin/env python

import io
import os
import re

from klepto.archives import file_archive
from setuptools import setup
from setuptools.command.build_py import build_py
from six import unichr

package_name = "pykakasi"
root_dir = os.path.abspath(os.path.dirname(__file__))


class genkanwadict(object):
    records = {}

    def run(self, src, dst):
        with open(src, 'rb') as f:
            for line in f:
                self.parsekdict(line.decode("utf-8"))
            f.close()
        self.kanwaout(dst)

    # for itaiji and kana dict

    def mkdict(self, src, dst):
        max_key_len = 0
        dic = {}
        with open(src, "rb") as f:
            for line in f:
                line = line.decode("utf-8").strip()
                if line.startswith(';;'):  # skip comment
                    continue
                if re.match(r"^$", line):
                    continue
                try:
                    (v, k) = (re.sub(r'\\u([0-9a-fA-F]{4})',
                                     lambda x: unichr(int(x.group(1), 16)), line)).split(' ')
                    dic[k] = v
                    max_key_len = max(max_key_len, len(k))
                except ValueError:
                    raise Exception("Cannot process dictionary line: ", line)
        d = file_archive(dst, dic, serialized=True)
        d['_max_key_len_'] = max_key_len
        d.dump()

    # for kanwadict

    def parsekdict(self, line):
        line = line.strip()
        if line.startswith(';;'):  # skip comment
            return
        (yomi, kanji) = line.split(' ')
        if ord(yomi[-1:]) <= ord('z'):
            tail = yomi[-1:]
            yomi = yomi[:-1]
        else:
            tail = ''
        self.updaterec(kanji, yomi, tail)

    def updaterec(self, kanji, yomi, tail):
        key = "%04x" % ord(kanji[0])
        if key in self.records:
            if kanji in self.records[key]:
                rec = self.records[key][kanji]
                rec.append((yomi, tail))
                self.records[key].update({kanji: rec})
            else:
                self.records[key][kanji] = [(yomi, tail)]
        else:
            self.records[key] = {}
            self.records[key][kanji] = [(yomi, tail)]

    def kanwaout(self, out):
        dic = file_archive(out, self.records, serialized=True)
        dic.dump()


class MyBuild(build_py):

    def generate_dictionaries(self):
        DICTS = [
            ('itaijidict.utf8', 'itaijidict3.db'),
            ('hepburndict.utf8', 'hepburndict3.db'),
            ('kunreidict.utf8', 'kunreidict3.db'),
            ('passportdict.utf8', 'passportdict3.db'),
            ('hepburnhira.utf8', 'hepburnhira3.db'),
            ('kunreihira.utf8', 'kunreihira3.db'),
            ('passporthira.utf8', 'passporthira3.db')
        ]
        kanwa = genkanwadict()
        dstdir = os.path.join(self.build_lib, 'pykakasi', 'data')
        if not os.path.exists(dstdir):
            os.mkdir(dstdir)
        for (src_f, pkl_f) in DICTS:
            src = os.path.join('src', 'data', src_f)
            dst = os.path.join(self.build_lib, 'pykakasi', 'data', pkl_f)
            if (os.path.exists(dst)):
                os.unlink(dst)
            kanwa.mkdict(src, dst)
        src = os.path.join('src', 'data', 'kakasidict.utf8')
        dst = os.path.join(self.build_lib, 'pykakasi', 'data', 'kanwadict4.db')
        if (os.path.exists(dst)):
            os.unlink(dst)
        kanwa.run(src, dst)

    def run(self):
        build_py.run(self)
        if not self.dry_run:
            self.generate_dictionaries()


def readme():
    with io.open(os.path.join(os.path.dirname(__file__), 'README.rst'), mode="r", encoding="UTF-8") as f:
        return f.read()


with open(os.path.join(root_dir, 'src', package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url


setup(name=package_name,
      version=version,
      description='Python implementation of kakasi - kana kanji simple inversion library',
      url=url,
      license=license,
      long_description=readme(),
      author=author,
      author_email=author_email,
      package_dir={'pykakasi': 'src/pykakasi'},
      packages=[package_name],
      provides=[package_name],
      scripts=["bin/kakasi"],
      include_package_data=True,
      package_data={'src/data': ['*.utf8']},
      tests_require=['pytest', 'coverage'],
      setup_requires=['six', 'klepto'],
      install_requires=['six', 'klepto'],
      extras_require={'dev': ['pytest']},
      cmdclass={'build_py': MyBuild},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Software Development :: Libraries :: Python Modules']
      )
