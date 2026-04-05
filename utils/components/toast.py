from django.template.loader import render_to_string


def create_toast(
    text: str,
    css_id: str | None = None,
    variant: str | None = None,
    title: str | None = None,
    icon: str | None = None,
    dismissible: bool = True,
    auto_dismiss: bool = True,
    delay: float = 5.0,
    **kwargs,
) -> str:
    """
    Render a Bootstrap 5 Toast component.

    Args:
        text: The main body text of the toast. HTML is safe.
        css_id: Optional ID for the toast element.
        variant: Optional style variant (e.g. 'primary', 'success', 'danger').
        title: Optional header title.
        icon: Optional Material Symbol icon name.
        dismissible: If True, adds a close button.
        auto_dismiss: Whether to auto-hide the toast (default: True).
        delay: Delay in seconds before auto-dismissing (default: 5.0).
        **kwargs: Additional HTML attributes to add to the toast element.

    Returns:
        The rendered HTML string.
    """

    # "error" is an alias for "danger"
    variant = "danger" if variant == "error" else variant

    # make sure the variant is valid
    variant_options = [
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
    ]
    if variant and variant not in variant_options:
        msg = f"Invalid variant '{variant}'. Must be one of {variant_options}."
        raise ValueError(msg)

    # override info, warning, danger, and success alert icons for consistency
    if variant == "info":
        icon = "info"
    elif variant == "warning":
        icon = "warning"
    elif variant == "danger":
        icon = "error"
    elif variant == "success":
        icon = "check_circle"

    # Map delay to milliseconds for usage in template
    attributes = kwargs.copy()
    attributes["data-bs-autohide"] = "false"

    # define custom attributes for auto-dismiss (used by our custom JS logic)
    if auto_dismiss:
        attributes["data-input-autodismiss"] = "true"

    context = {
        "text": text,
        "variant": variant,
        "title": title,
        "icon": icon,
        "dismissible": dismissible,
        "auto_dismiss": auto_dismiss,
        "delay_ms": int(delay * 1000),
        "css_id": css_id,
        "attributes": attributes,
    }
    return render_to_string("components/toast/toast.html", context)
