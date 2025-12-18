from cloudinary.utils import cloudinary_url


def generate_optimized_url(
    public_id: str,
    fmt: str = "auto",
    quality: str = "auto",
    fetch_format: str = "auto",
    width: int | None = None,
    height: int | None = None,
    crop: str | None = None,
    secure: bool = True,
) -> str:
    """
    Wraps Cloudinary's `cloudinary_url` to generate an optimized image URL
    with sensible defaults (f_auto, q_auto) while allowing parameter overrides.

    Parameters
    ----------
    public_id : str
        The Cloudinary public ID of the asset (e.g., "sample.jpg").
    fmt : str, optional
        Format transformation (default: "auto").
        Example: "jpg", "png", "webp", "auto".
    quality : str, optional
        Quality transformation (default: "auto").
        Example: "auto", "80", "100".
    fetch_format : str, optional
        Fetch format transformation (default: "auto").
        Example: "auto", "webp", "avif".
    width : int, optional
        Width transformation (default: None).
    height : int, optional
        Height transformation (default: None).
    crop : str, optional
        Crop mode (default: None).
        Example: "fill", "fit", "scale", "thumb".
    secure : bool, optional
        Whether to generate a secure HTTPS URL (default: True).

    Returns
    -------
    str
        Optimized Cloudinary image URL.

    Example
    -------
    >>> generate_optimized_url("sample.jpg", width=400, height=300, crop="fill")
    'https://res.cloudinary.com/<cloud_name>/image/upload/f_auto,q_auto,w_400,h_300,c_fill/sample.jpg'
    """

    if not public_id:
        return public_id

    # Build transformation dictionary
    transformations: dict[str, str | int] = {
        "format": fmt,
        "quality": quality,
        "fetch_format": fetch_format,
    }

    if width:
        transformations["width"] = width
    if height:
        transformations["height"] = height
    if crop:
        transformations["crop"] = crop

    url, _ = cloudinary_url(public_id, secure=secure, **transformations)

    return str(url)
