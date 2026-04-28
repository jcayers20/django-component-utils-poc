from django.template.loader import render_to_string
from pydantic.dataclasses import dataclass


@dataclass
class Alert:
    text: str
    css_id: str | None = None
    variant: str = "primary"
    title: str | None = None
    icon: str | None = None
    footer: str | None = None
    dismissible: bool = True
    auto_dismiss: bool = False
    delay: float = 5.0  # provide in seconds
    attributes: dict[str, str] | None = None

    def to_html(self) -> str:
        context = {"alert": self}
        return render_to_string("components/alert/alert.html", context)


def create_alert(
    text: str,
    css_id: str | None = None,
    variant: str = "primary",
    title: str | None = None,
    icon: str | None = None,
    footer: str | None = None,
    dismissible: bool = True,
    auto_dismiss: bool = False,
    delay: float = 5.0,
    as_html: bool = False,
    **kwargs,
) -> str | Alert:
    """
    Render a Bootstrap 5 Alert component.

    Args:
        text: The main body text of the alert. HTML is safe.
        css_id: Optional ID for the alert element.
        variant: The Bootstrap alert variant. Must be one of 'primary', 'secondary', 'success', 'danger', 'error', 'warning', 'info', 'light', or 'dark'.
        title: Optional title for the alert.
        icon: Optional Material Symbol icon name.
        footer: Optional footer text.
        dismissible: If True, adds a close button.
        auto_dismiss: If True, the alert will auto-dismiss after `delay` seconds. Defaults to False.
        delay: Number of seconds to wait before auto-dismissing. Defaults to 5.0.
        **kwargs: Additional HTML attributes to add to the alert element.

    Returns:
        The rendered HTML string if `as_html` is True, otherwise an Alert object.
    """

    # cast variant to lower-case for consistency
    variant = variant.lower()

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
    if variant not in variant_options:
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

    # prepare attributes and auto-dismiss data attributes
    attributes = kwargs.copy()
    if auto_dismiss:
        attributes["data-input-autodismiss"] = "true"
        attributes["data-input-delay-ms"] = str(int(delay * 1000))

    # create the alert
    alert = Alert(
        text=text,
        css_id=css_id,
        variant=variant,
        title=title,
        icon=icon,
        footer=footer,
        dismissible=dismissible,
        auto_dismiss=auto_dismiss,
        delay=int(delay * 1000),
        attributes=attributes,
    )

    # return the alert in the desired format
    return alert.to_html() if as_html else alert
