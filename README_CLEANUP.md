# TravelGo Project Cleanup Summary

## Scripts Moved
- All admin/dev scripts moved to `scripts/` folder:
  - `print_cab_images.py`
  - `update_service_images.py`
  - `copy_service_images.py`
  - `rename_images_to_png.py`
  - `seed_services.py`

## Modularization Suggestion
- For further modularization, split `app/routes.py` into:
  - `routes/auth.py` (login, signup, logout)
  - `routes/booking.py` (booking, payment, confirmation)
  - `routes/services.py` (service listing, search)
  - `routes/dashboard.py` (user dashboard, profile)
- Group templates by feature in subfolders if desired.

## Next Steps
- Delete the original scripts from the project root if not needed.
- Review and modularize routes as above for maintainability.
- Continue template/static cleanup as needed.
