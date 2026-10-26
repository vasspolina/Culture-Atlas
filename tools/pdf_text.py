#!/usr/bin/env python3
"""Print a PDF's text, one "=====PAGE n=====" header per page (macOS PDFKit; no extra packages).

Usage: python3 tools/pdf_text.py file.pdf [first_page [last_page]]   (pages count from 1, PDF order)
A scan with no text layer prints empty pages.
"""
import sys

import Quartz
from Foundation import NSURL

doc = Quartz.PDFDocument.alloc().initWithURL_(NSURL.fileURLWithPath_(sys.argv[1]))
if doc is None:
    sys.exit('cannot open ' + sys.argv[1])
first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
last = int(sys.argv[3]) if len(sys.argv) > 3 else doc.pageCount()
for i in range(first - 1, min(last, doc.pageCount())):
    print(f'=====PAGE {i + 1}=====')
    print(doc.pageAtIndex_(i).string() or '')
