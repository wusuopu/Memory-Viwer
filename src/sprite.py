#!/usr/bin/env python
# encoding: utf-8

import os


BASE_DIR = os.path.realpath(os.path.join(__file__, '..', 'static'))
IMAGE_DIR = os.path.join(BASE_DIR, 'image')
CSS_DIR = os.path.join(BASE_DIR, 'css')
JS_DIR = os.path.join(BASE_DIR, 'js')
VENDOR_JS_DIR = os.path.join(BASE_DIR, 'vendor', 'js')

def bundle_assets():
    with open(os.path.join(CSS_DIR, 'bundle.css'), 'w') as out:
        out.write('/*icon image*/\n')
        with open(os.path.join(BASE_DIR, 'vendor/css/element-plus.css'), 'r') as fp:
            out.write(fp.read())
        out.write('/*==========================*/\n')
        with open(os.path.join(CSS_DIR, 'main.css'), 'r') as fp:
            out.write(fp.read())

    js_files = [
        "jquery-3.7.1.js",
        "vue.global.prod.js",
        "vuex.global.prod.js",
        "vue-router.global.prod.js",
        "lodash-4.17.21.js",
        "tailwindcss-3.4.5.js",
        "element-plus.js",
        "element-plus-icons.js",
    ]
    with open(os.path.join(JS_DIR, 'bundle.js'), 'w') as out:
        for f in js_files:
            print('concat %s' % (f))
            with open(os.path.join(VENDOR_JS_DIR, f), 'r') as fp:
                out.write(fp.read())
                out.write('\n\n//==========\n')

        with open(os.path.join(JS_DIR, 'main.js'), 'r') as fp:
            out.write(fp.read())


def main():
    bundle_assets()

if __name__ == '__main__':
    main()
