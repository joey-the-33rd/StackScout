# TODO: Strict Amount Parsing Implementation

## Steps to Complete:

1. [ ] Update `parse_salary_amount` method in `job_search_storage.py`:
   - [ ] Replace `if not amount_str: return None` with explicit None check that raises ValueError
   - [ ] Convert input to string and strip whitespace
   - [ ] Check if stripped string is empty and raise ValueError
   - [ ] Use the stripped string for currency symbol removal and further processing

2. [ ] Verify changes work correctly
3. [ ] Test with various input scenarios (None, empty string, whitespace-only, valid amounts)
4. [ ] Ensure existing functionality is not broken

## Current Status: Starting implementation
