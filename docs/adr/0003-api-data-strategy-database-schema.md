# ADR 0003: FPL API Data Strategy & Database Schema

## Status
Accepted

## Context
Fantasy Premier League (FPL) provides raw JSON payloads containing extensive, nested, and often redundant data. To build a robust, reproducible expected points (xP) projection model and run Mixed-Integer Linear Programming (MILP) optimizations, we need a clean, structured relational database schema in PostgreSQL. 

We must decide:
1. What endpoints to ingest.
2. What fields to normalize and store in relational tables.
3. What fields to discard (e.g., transient UI config or raw averages).
4. How to resolve terminology overlaps (e.g. `team` meaning "Club" vs. "Manager Squad").

---

## Decision

We will standardize database columns and parameters, store a normalized relational schema in PostgreSQL, and maintain the raw JSON responses in `data/raw/` as a rate-limit shield and offline fallback.

### Terminology Rules
*   **`entry_id`**: Always represents the manager's team profile (e.g. `6025459`).
*   **`team_id`** (or `club_id`): Always represents a Premier League Club (e.g. `1` for Arsenal).
*   **`position_id`**: General pitch role (1=GKP, 2=DEF, 3=MID, 4=FWD). Maps to `element_type` in the FPL API.
*   **`lineup_index`**: Squad slot within the 15-player team (1 to 15). Maps to `position` in the FPL picks.

---

### Database Schema Mapping

#### 1. Clubs (`clubs` table)
*   **Source:** `/bootstrap-static/` (`teams` list)
*   **Stored in DB:**
    *   `id` (`INT PRIMARY KEY`): Club ID.
    *   `name` (`VARCHAR`): e.g., "Arsenal".
    *   `short_name` (`VARCHAR`): e.g., "ARS".
    *   `strength` (`INT`): FPL overall difficulty rating (1 to 5).
    *   `strength_overall_home`, `strength_overall_away`, `strength_attack_home`, `strength_attack_away`, `strength_defence_home`, `strength_defence_away` (`INT`): Team quality vectors for modeling.
*   **Discarded:** `code`, `draw`, `loss`, `win`, `played`, `points`, `position` (current league standing), `team_division`, `link_url`, `pulse_id`, `unavailable`, `form`.

#### 2. Positions (`positions` lookup / enum)
*   **Source:** `/bootstrap-static/` (`element_types` list)
*   **Stored in DB:**
    *   `id` (`INT PRIMARY KEY`): 1=GKP, 2=DEF, 3=MID, 4=FWD.
    *   `singular_name` (`VARCHAR`): e.g., "Goalkeeper".
    *   `singular_name_short` (`VARCHAR`): e.g., "GKP".
*   **Discarded:** `plural_name`, `plural_name_short`, `ui_shirt_specific`, `sub_positions_locked`, `element_count`, `squad_select`, `squad_min_play`/`squad_max_play` (hardcoded directly in Python MILP rules instead).

#### 3. Gameweeks (`gameweeks` table)
*   **Source:** `/bootstrap-static/` (`events` list)
*   **Stored in DB:**
    *   `id` (`INT PRIMARY KEY`): 1 to 38.
    *   `name` (`VARCHAR`): e.g., "Gameweek 1".
    *   `deadline_time` (`TIMESTAMP WITH TIME ZONE`): Ingestion and planning lockout limit.
    *   `finished` (`BOOLEAN`): If the gameweek matches have concluded.
    *   `is_current` (`BOOLEAN`): Active gameweek indicator.
    *   `is_next` (`BOOLEAN`): Next target planning horizon.
*   **Discarded:** `release_time`, `average_entry_score`, `data_checked`, `highest_scoring_entry`, `deadline_time_epoch`, `deadline_time_game_offset`, `highest_score`, `is_previous`, `cup_leagues_created`, `h2h_ko_matches_created`, `can_enter`, `can_manage`, `released`, `ranked_count`, `overrides`, `chip_plays`, `most_selected`, `most_transferred_in`, `top_element`, `top_element_info`, `transfers_made`, `most_captained`, `most_vice_captained`.

#### 4. Players (`players` table)
*   **Source:** `/bootstrap-static/` (`elements` list)
*   **Stored in DB:**
    *   `id` (`INT PRIMARY KEY`): Player ID.
    *   `first_name`, `second_name`, `web_name` (`VARCHAR`).
    *   `club_id` (`INT REFERENCES clubs(id)`): Maps to `team` in FPL elements.
    *   `position_id` (`INT REFERENCES positions(id)`): Maps to `element_type` in FPL elements.
    *   `now_cost` (`INT`): Current FPL cost in £0.1m increments.
    *   `status` (`VARCHAR(5)`): 'a' (available), 'i' (injured), 'd' (doubtful), etc.
    *   `chance_of_playing_next_round`, `chance_of_playing_this_round` (`INT`, nullable).
    *   `news` (`TEXT`), `news_added` (`TIMESTAMP WITH TIME ZONE`, nullable).
    *   `selected_by_percent` (`NUMERIC(4, 1)`): Global ownership percentage.
    *   `corners_and_indirect_freekicks_order`, `direct_freekicks_order`, `penalties_order` (`INT`, nullable): Set-piece orders.
    *   **Season Totals (For Cross-Validation):** All aggregate totals (`total_points`, `minutes`, `goals_scored`, `assists`, `clean_sheets`, `goals_conceded`, `own_goals`, `penalties_saved`, `penalties_missed`, `yellow_cards`, `red_cards`, `saves`, `bonus`, `bps`, `influence`, `creativity`, `threat`, `ict_index`, `clearances_blocks_interceptions`, `recoveries`, `tackles`, `defensive_contribution`, `starts`, `expected_goals`, `expected_assists`, `expected_goal_involvements`, `expected_goals_conceded`).
*   **Discarded:** `code`, `team_code`, `squad_number`, `photo`, `removed`, `birth_date`, `region`, `team_join_date`, `has_temporary_code`, `opta_code`, `can_transact`, `can_select`, `cost_change_event`, `cost_change_event_fall`, `cost_change_start`, `cost_change_start_fall`, `price_change_percent`, `dreamteam_count`, `in_dreamteam`, `ep_this`, `ep_next`, `form`, `value_form`, `value_season`, `points_per_game`, `scout_risks`, `scout_news_link`, and all ranks/per-90 variables.

#### 5. Fixtures (`fixtures` table)
*   **Source:** `/fixtures/`
*   **Stored in DB:**
    *   `id` (`INT PRIMARY KEY`).
    *   `gameweek_id` (`INT REFERENCES gameweeks(id)`): Maps to `event`.
    *   `kickoff_time` (`TIMESTAMP WITH TIME ZONE`).
    *   `home_club_id` (`INT REFERENCES clubs(id)`): Maps to `team_h`.
    *   `away_club_id` (`INT REFERENCES clubs(id)`): Maps to `team_a`.
    *   `finished` (`BOOLEAN`).
    *   `started` (`BOOLEAN`).
    *   `team_h_score`, `team_a_score` (`INT`, nullable).
    *   `team_h_difficulty`, `team_a_difficulty` (`INT`).
    *   `raw_stats` (`JSONB`, nullable): Stores raw `'stats'` array.
*   **Discarded:** `code`, `finished_provisional`, `provisional_start_time`, `minutes`, `pulse_id`.

#### 6. Player Gameweek Performances (`player_gameweek_performances` table)
*   **Source:** `/element-summary/{player_id}/` (`history` list) & `/event/{gw_id}/live/`
*   **Stored in DB:**
    *   `id` (`BIGSERIAL PRIMARY KEY`).
    *   `player_id` (`INT REFERENCES players(id)`).
    *   `fixture_id` (`INT REFERENCES fixtures(id)`).
    *   `gameweek_id` (`INT REFERENCES gameweeks(id)`).
    *   `opponent_club_id` (`INT REFERENCES clubs(id)`).
    *   `was_home` (`BOOLEAN`).
    *   `kickoff_time` (`TIMESTAMP WITH TIME ZONE`).
    *   `team_h_score`, `team_a_score` (`INT`, nullable).
    *   All performance details (`minutes`, `total_points`, `goals_scored`, `assists`, `clean_sheets`, `goals_conceded`, `own_goals`, `penalties_saved`, `penalties_missed`, `yellow_cards`, `red_cards`, `saves`, `bonus`, `bps`, `influence`, `creativity`, `threat`, `ict_index`, `clearances_blocks_interceptions`, `recoveries`, `tackles`, `defensive_contribution`, `starts`, `expected_goals`, `expected_assists`, `expected_goal_involvements`, `expected_goals_conceded`).
    *   `price` (`INT`): Maps to `value` (historical player cost at that fixture).
    *   `selected` (`INT`): Ownership count.
    *   `transfers_balance`, `transfers_in`, `transfers_out` (`INT`).
*   **Discarded:** `modified`.

#### 7. Player Past Seasons (`player_past_seasons` table)
*   **Source:** `/element-summary/{player_id}/` (`history_past` list)
*   **Stored in DB:**
    *   `player_id` (`INT REFERENCES players(id)`).
    *   `season_name` (`VARCHAR(20)`): e.g., "2023/24".
    *   `start_cost`, `end_cost` (`INT`).
    *   All seasonal aggregate stats matching the performance fields.
    *   *Primary Key:* `(player_id, season_name)`.
*   **Discarded:** `element_code`.

#### 8. User Squad Picks (`user_squad_picks` table)
*   **Source:** `/my-team/{entry_id}/` (`picks` list) & `/entry/{entry_id}/event/{gw_id}/picks/`
*   **Stored in DB:**
    *   `entry_id` (`INT`): Manager profile ID.
    *   `gameweek_id` (`INT REFERENCES gameweeks(id)`).
    *   `player_id` (`INT REFERENCES players(id)`).
    *   `lineup_index` (`INT`): Maps to `position` (squad slot 1 to 15).
    *   `multiplier` (`INT`): 0=bench, 1=starter, 2=captain, 3=triple captain.
    *   `is_captain`, `is_vice_captain` (`BOOLEAN`).
    *   `purchase_price`, `selling_price` (`INT`).
    *   *Primary Key:* `(entry_id, gameweek_id, player_id)`.

#### 9. User State (`user_state` table)
*   **Source:** `/my-team/{entry_id}/`
*   **Stored in DB:**
    *   `entry_id` (`INT PRIMARY KEY`).
    *   `bank` (`INT`).
    *   `value` (`INT`).
    *   `free_transfers` (`INT`).
    *   `active_chip` (`VARCHAR(20)`, nullable).
*   **Discarded:** `cost` (redundant with budget calculations), `status`, `limit`, `made` (available via free_transfers calculations).
