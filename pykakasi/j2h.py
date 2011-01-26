# -*- coding: utf-8 -*-
#  j2h.py
#
# Copyright 2011 Hiroshi Miura <miurahr@linux.com>
#
#
# * KAKASI (Kanji Kana Simple inversion program)
# * $Id: jj2.c,v 1.7 2001-04-12 05:57:34 rug Exp $
# * Copyright (C) 1992
# * Hironobu Takahashi (takahasi@tiny.or.jp)
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either versions 2, or (at your option)
# * any later version.
# *
# * This program is distributed in the hope that it will be useful
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with KAKASI, see the file COPYING.  If not, write to the Free
# * Software Foundation Inc., 59 Temple Place - Suite 330, Boston, MA
# * 02111-1307, USA.
# */

from jisyo import jisyo

class J2H (object):

    kanwa = None

    cl_table = [
	"","aiueow", "aiueow", "aiueow", "aiueow", "aiueow", "aiueow", "aiueow",
	"aiueow", "aiueow", "aiueow", "k", "g", "k", "g", "k", "g", "k", "g", "k",
	"g", "s", "zj", "s", "zj", "s", "zj", "s", "zj", "s", "zj", "t", "d", "tc",
	"d", "aiueokstchgzjfdbpw", "t", "d", "t", "d", "t", "d", "n", "n", "n", "n",
	"n", "h", "b", "p", "h", "b", "p", "hf", "b", "p", "h", "b", "p", "h", "b",
	"p", "m", "m", "m", "m", "m", "y", "y", "y", "y", "y", "y", "rl", "rl",
	"rl", "rl", "rl", "wiueo", "wiueo", "wiueo", "wiueo", "w", "n", "v", "k",
	"k", "", "", "", "", "", "", "", "", ""]

    def __init__(self):
        self.kanwa = jisyo()  

    def isCletter(self, l, c):
        if (ord(u"ぁ") <= ord(c) and  ord(c) <= 0x309f) and (  l in self.cl_table[ord(c) - ord(u"ぁ")-1]):
            return True
        return False

    def convert(self, text):
        max_len = 0
        match_more = False
        Hstr = ""
        table = self.kanwa.load_jisyo(text[0])
        if table is None:
            return ("", 0, False)
        for (k,v) in table.iteritems():
            length = len(k)
            if len(text) >= length:
                if text.startswith(k):
                    for  (yomi, tail) in v:
                        if max_len <= length:
                            if tail is '':
                                Hstr = yomi
                                max_len = length
                            elif self.isCletter(tail, text[length]):
                                Hstr=''.join([yomi,text[length]])
                                max_len = length
            elif text[2:].startswith(k):
                    match_more = True

        return (Hstr, max_len, match_more)