# Tailwind System Checklist

- Tailwind version and build integration are known.
- Source/class detection covers all files that contain class names.
- Dynamic class names are replaced with complete static alternatives or safelisted/source-included intentionally.
- Tokens are centralized and documented by usage.
- Repeated class clusters are converted to components or variant helpers.
- Responsive behavior is tested at target breakpoints.
- Focus, hover, active, disabled, loading, error, and success states exist where needed.
- Production CSS is checked for missing classes and excessive output.
