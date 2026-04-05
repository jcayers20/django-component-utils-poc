# Data-Star Django Component Implementation Status

## Overview
We are building a library of reusable, backend-driven UI components for Django using Datastar and Bootstrap 5. The components are implemented as Python utility functions that render HTML strings, designed to be used both in standard Django templates and in Datastar SSE patches.

## Architecture
- **Location**: `utils/components/*.py` contains the Python logic.
- **Templates**: `templates/components/<component>/<component>.html`.
- **Assets**: CSS/JS for components reside in `static/css/components/` and `static/js/components/`.
- **Global Assets**:
  - `templates/base.html` includes the global `toasts.js` script and `#toast-container`.
  - Material Symbols Outlined is used for icons.
  - Bootstrap 5 via CDN/Local static.

## Components Implemented

### 1. Alert (`utils.components.alert`)
- **Features**: Variants (primary, danger, etc.), Icons (auto-mapped or custom), Dismissible, Thick left border styling, optional auto-dismiss with progress indicator (disabled by default).
- **Usage**:
  ```python
  from utils.components import alert
  html = alert.create_alert(
      text="Something happened!",
      variant="success",
      icon="check_circle",
      dismissible=True,
      auto_dismiss=True,  # default is False
      delay=4.5,          # seconds
  )
  ```

### 2. Toast (`utils.components.toast`)
- **Features**:
  - Auto-dismiss with visual progress bar (CSS animation).
  - Hover to pause dismissal time.
  - Stacking support via global `#toast-container`.
  - Integration with Datastar `mode='append'` patches.
- **Implementation**:
  - Uses `MutationObserver` in `static/js/components/toast.js` to auto-initialize Bootstrap toasts when they appear in the DOM.
  - Custom CSS (`static/css/components/toast.css`) handles the progress bar animation.
  - Python wrapper maps `delay` to animation duration.
- **Usage**:
  ```python
  from utils.components import toast
  html = toast.create_toast(
      text="Action completed.",
      variant="info",
      auto_dismiss=True,
      delay=5.0
  )
  ```

## Pending / Next Steps
- **Additional Components**: Consider Cards, Modals, or Badges next.
- **Testing**: Expand `component_examples` app with more interactive showcases.
- **Documentation**: Add docstrings or expanding `docs/` with usage guides.

## Key Implementation Details
- **Toasts**: Do **not** wrap toasts in a container within the component output. Push them to the global `#toast-container` in `base.html`.
- **Auto-Init**: We prefer `MutationObserver` over manual initialization scripts for smoother Datastar integration.
