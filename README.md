# yaml-cli

A tool for super basic YAML processing and editing.

## Description

I needed a CLI YAML processor to edit files, specifically Docker Compose files. Every other tool I tried (e.g `yq`) had shortcomings such as not preserving comments or the original document order, which made them unsuitable for my purposes. Hence I hastily produced my own shitty CLI YAML processor and editor.

## Requirements

* Python 3
* [ruamel.yaml library](https://bitbucket.org/ruamel/yaml/src/default/)

## TODO

- [ ] A better README
- [ ] Documentation
- [ ] Unit tests
