# Bonaparte Stories: weekly research run (vidIQ)

Runs once a week, separately from the daily run. It never renders or publishes videos.
Its job is to feed the daily run through INSIGHTS.md and the order of `upcoming_series` in state.json.

## Budget
vidIQ gives 150 credits per month (reset on the 2nd). Spend at most 30 credits per run (about 6 paid calls).
Call `vidiq_balance` first (free). If the balance is under 30, do only step 2 (free) and step 5.

## Steps
1. `git pull`. Read STYLE.md, INSIGHTS.md, state.json and the last report in research/.
2. Channel performance (free if the channel is connected): `vidiq_user_channels`; if the Bonaparte Stories channel is listed, read its recent videos and stats (views, likes, comments per part) and note which parts and hooks did best and worst. If no channel is connected, say so in the report.
3. What is breaking out (about 3 paid calls): `vidiq_outliers` (keyword "Napoleon", Shorts, last month), `vidiq_instagram_tiktok_outlier_search` (Napoleon history stories, English-speaking, last 30 days), and one of: `vidiq_keyword_research` rising (niche "Napoleon Bonaparte history") or `vidiq_outliers` on the battle of the next series.
4. Optional (at most 2 paid calls): `vidiq_video_transcript` of the most relevant narrated outlier, to study its hook and structure. Learn techniques only; never copy wording or stories.
5. Write `research/<YYYY-MM-DD>.md` (what broke out, numbers, lessons). Update INSIGHTS.md: keep it short, replace rules that the data contradicts, never more than ~15 rules. You may reorder `upcoming_series` in state.json (never touch `current_series`, `next_part` or `posted`), and add a new series idea when the data clearly supports it.
6. Commit and push to main. End with a short summary for the owner: top 3 findings, what changed in INSIGHTS.md and the series order, credits used.
