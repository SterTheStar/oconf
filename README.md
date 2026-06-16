# OConf

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.6%2B-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<p align="center">
  <img src="icons/icon.png" alt="OConf logo" width="128" />
</p>

<p align="center">
  OpenCode configuration manager with a polished Qt interface for editing `~/.config/opencode/opencode.jsonc`.
</p>

## Overview

OConf is a desktop tool for managing OpenCode configuration through a clear, dark UI built with Python and PySide6. It is designed to make advanced configuration easier to inspect, edit, validate, and restore without working directly in the raw JSONC file.

## What it does

- Edit general settings such as model, `small_model`, shell, and log level
- Manage providers and models through structured forms
- Configure agents and MCP servers
- Edit the raw JSONC when needed
- Create backups automatically before saving
- Validate the configuration and surface issues quickly

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.11 or newer
- PySide6 6.6 or newer
- json5 0.9.14 or newer

## Notes

- The application reads and writes `~/.config/opencode/opencode.jsonc`
- Backups are created automatically before each save
- Restart OpenCode after saving changes to apply them
