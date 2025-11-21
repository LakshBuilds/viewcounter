# Progress Notes

## Environment & Setup
- Installed project dependencies using `pip install -r requirements.txt`.
- Created a clean `.streamlit/config.toml` (ASCII only) to resolve Streamlit config parsing errors and verified the server runs locally.
- Added a `.env` file (outside version control) with Apify, Supabase, and Clerk credentials so `load_dotenv()` can configure the app automatically.
- Identified and killed lingering Python/Streamlit processes to free the default port when necessary.

## Streamlit Runtime Fixes
- Resolved PowerShell command issues when launching Streamlit by activating the virtualenv and invoking `python -m streamlit run app.py`.
- Documented the need to include the `.py` extension when running `streamlit run app.py`.

## Supabase Persistence Improvements
- Added logic to skip saving archived/restricted reels to Supabase to prevent invalid rows from overwriting good data.
- Refined `save_data_to_supabase()` to:
  - Filter out `skip_supabase_save` items.
  - Preload existing records for the incoming IDs/shortcodes only.
  - Detect global duplicate IDs and update those rows instead of inserting, eliminating primary-key (`reels_pkey`) violations.
  - Continue user-specific updates while preserving payout values.

## Refresh & Archival Handling
- Introduced `mark_item_as_archived()` and enhanced `refresh_all_reels()` to detect Apify responses that contain `error` / `errorDescription` (e.g., Instagram restricted/archived reels).
- Preserved the last known metrics/payouts for those reels, flagged them as archived, and recorded a summary for UI display.
- Displayed the archived/restricted summary under a collapsible warning panel in the dashboard so users know which reels were skipped during refresh.

## User Guidance
- Explained why Clerk errors appeared (missing `.env` values) and how to fix them.
- Clarified that archived Instagram reels cannot be refreshed because Apify only returns restricted/error responses; the dashboard now keeps prior data and indicates the archived status instead of saving empty rows.

