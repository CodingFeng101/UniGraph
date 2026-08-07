#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import uvicorn

from backend.core.registrar import register_app

app = register_app()


if __name__ == '__main__':
    uvicorn.run('backend.main:app', host='0.0.0.0', port=8000, reload=True)
