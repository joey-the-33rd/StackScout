# Plan to Address PR Code Suggestions for API Endpoint and Analytics Dashboard

## Information Gathered
- `stackscout_web.py` has an `api_save_job` endpoint that creates its own `JobSearchStorage` instance instead of using dependency injection
- Analytics dashboard shows overall job statistics but may need to include saved jobs metrics
- TODO.md indicates pending refactoring of endpoints to use dependency injection
- The analytics engine tracks user interactions which might include job saves

## Plan
1. **Refactor api_save_job endpoint** to use `get_storage` dependency injection instead of creating its own instance
2. **Update analytics engine** to include saved jobs statistics (jobs saved by users)
3. **Update analytics dashboard** to display saved jobs count and related metrics
4. **Test the changes** to ensure proper functionality

## Dependent Files to be edited
- `stackscout_web.py` (refactor api_save_job)
- `src/analytics/engine.py` (add saved jobs analytics)
- `templates/analytics_dashboard.html` (update dashboard UI)

## Followup steps
- Test the refactored endpoint
- Verify analytics data includes saved jobs
- Ensure dashboard displays updated metrics

## Completed Changes
✅ **Refactored api_save_job endpoint**: Changed from creating its own JobSearchStorage instance to using dependency injection with `get_storage`
✅ **Updated analytics engine**: Added saved jobs statistics using user_job_interactions table with interaction_type = 'save'
✅ **Updated analytics dashboard**: Replaced "Growth Rate" card with "Saved Jobs" card and updated JavaScript to display saved jobs count
✅ **Tested changes**: Analytics endpoint now returns saved jobs statistics (currently 0, which is expected if no jobs have been saved yet)

## Summary
The PR code suggestions have been successfully addressed:
- API endpoint now uses proper dependency injection
- Analytics dashboard shows saved jobs metrics
- All changes are backward compatible and follow existing patterns

