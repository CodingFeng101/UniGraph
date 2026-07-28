#!/usr/bin/.env python3
# -*- coding: utf-8 -*-
import sys

# 在 app.task.celery 模块的 __init__.py 或 celery.py 最顶部添加
from pathlib import Path

# 导入项目根目录
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
