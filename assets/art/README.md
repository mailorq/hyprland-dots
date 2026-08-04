# Fata Morgana art assets

`fata-morgana/` contains normalized, user-supplied reference art for local
desktop use. The raw `pictures/` directory remains ignored and untouched.

Each committed JPEG is orientation-corrected, converted to sRGB RGB, stripped
of metadata, and capped at a 2048 px long edge without cropping or upscaling.
The manifest records the source and generated checksums, dimensions, reusable
roles, and the small subset suitable for gentle 16:9 wallpaper crops.

The artwork has not been licence-audited for public redistribution. Confirm the
rights and artist attribution before publishing a repository containing it.
