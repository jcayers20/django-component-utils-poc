# Data-Star Components API

## Introduction

This Django application is meant to serve as a place for me to develop a set of
reusable Python utilities for creating common web components. These utilities
are designed to be easily integrated into Django projects, promoting code reuse
and consistency across different web applications.

## Frameworks

- Django - Python web framework
- Ruff - code linting and formatting
- UV - dependency management
- Bootstrap 5.0 - CSS and JS for styling and interactive components
- data-star 1.0 - JS for backend-driven features and dynamic content rendering
- Material Symbols - icon library

## File Structure

- `component_examples/` - Django app providing playground examples for reusable web components
- `config/` - Configuration files for the Django project
- `docs/` - Documentation files for the project
- `static/` - Static files such as CSS, JavaScript, and images
- `templates/` - HTML template files for the Django project
- `templates/components/` - HTML template files for reusable web components
- `utils/` - Utility modules that can be used throughout the project
- `utils/components/` - Utility modules for creating reusable web components

## Design Principles

- Components should be created using functions rather than classes.
- Components should be modular and self-contained.
- Components should be built with a focus on generalization and reusability.
- Components should be easily composable and configurable.
- Components should be well-documented, with docstrings useful for both humans and AI agents.
- Components should have clear and consistent naming conventions.
- Components should have styling rooted in Bootstrap but may be customized if it adds value.
- Components should be accessible and follow web accessibility standards.
- Reactivity in components should be handled via data-star using generalized URL's wherever possible.
